# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 15 — null-safety & error handling.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# MERGED WEEK, and it DEEPENS four things rather than introducing them. The
# `_SCOPE_RULES` table deliberately omits `?.`-past-week-7, `??`, `!`, `try`,
# `catch` and `throw`, because:
#
#   week 6  — `!` and `??` arrive the day noUncheckedIndexedAccess turns on
#   week 7  — `?.` on optional object members
#   week 8  — `try` at the parsing boundary
#   week 9  — `catch`, `throw`, `new Error`, `instanceof Error`, and a first
#             generic `Result<T>` as a discriminated union
#   week 11 — classes, which is what makes lesson 6 (custom Error subclasses)
#             possible at all
#
# Lessons 3, 4, 5 and 7 must therefore be written as "you have been using this;
# here is the whole rule", not as first contact. Only lessons 8-9 are new ground.
#
# ---------------------------------------------------------------------------
# THE ONE GENUINELY NEW HAZARD: `JSON.parse` returns `any`.
#
# It is the only place in the whole course where the type system is silently
# switched off, and it cannot be demonstrated with a `diagnose` — the point is
# that there is NO error. So lesson 8 uses `_retype` (the kind that exists for
# exactly this) and lesson 9 earns the type back with a real guard. That pairing
# is the week's payload, and the capstone is the two of them applied.
#
# `JSON.parse` also cannot be gated by the scope lint before this week without
# checking: verified clear across weeks 1-14 before ("JSON.parse(", 15) landed.
# ---------------------------------------------------------------------------

# --- Week 15 --------------------------------------------------------------
_WEEKS.append(_week(
    15, 4, _M4,
    "Null-Safety & Error Handling",
    "Handle the value that isn't there (?., ??, strict null checks) and the call that went wrong (try/catch and the Result pattern) — then meet untrusted data, where JSON.parse hands back `any` and you have to earn a type.",
    """
Two questions that turn out to be one week:

* **The value is not there.** No entry with that id, no `tag` on that object, the
  array was empty.
* **Getting it went wrong.** The text would not parse, the number was not a
  number, the file was not JSON.

You have been handling both since week 6, in pieces — `??` when
`noUncheckedIndexedAccess` turned on, `?.` in week 7, `try` in week 8,
`throw` and `instanceof Error` in week 9. This week joins them up and adds the
part nobody has faced yet.

## The part nobody has faced yet

```ts
const data = JSON.parse('{"desc":"coffee","cents":325}');

console.log(data.desc);              // "coffee"
console.log(data.nope.deeper.still); // compiles fine. Crashes at runtime.
```

No error. No squiggle. `JSON.parse` is declared to return **`any`**, and `any`
switches the type system off for everything downstream of it. Every guarantee
this course has built for fourteen weeks stops at that line.

That is not a flaw in the declaration — it is honest. TypeScript genuinely does
not know what is in that string. What is *not* honest is what most code does
next:

```ts
const data = JSON.parse(text) as Entry;    // a claim, checked by nobody
```

Week 12 taught you what `as` is worth. This is a lie with a straight face, and it
is how a `cents` field containing `"lots"` ends up inside a program whose types
all say `number`.

The honest move is two steps, and lessons 8 and 9 are those steps:

```ts
const raw: unknown = JSON.parse(text);     // 1. admit you know nothing
if (!isEntry(raw)) {                        // 2. check, and earn the type
  return { ok: false, error: "not an entry" };
}
raw.cents.toFixed(2);                       // now this is a fact
```

## What else is here

**Null-safety, properly.** `null` versus `undefined` and where each comes from;
`x?: T` versus `x: T | undefined` (they are genuinely different); the whole
`?.` and `??` story including the `||` trap; and when a `!` is *earned* rather
than wished.

**Errors, properly.** Why `catch (e)` gives you `unknown` and what to do about
it; custom `Error` subclasses, which need week 11's classes; and the **`Result`
pattern** — returning failure instead of throwing it, which is the right answer
more often than people expect.

⏱️ Budget about **eleven hours**. This is the longest week in the month.
""",
    objectives=[
        "Say where `null` and `undefined` each come from, and pick a convention",
        "Distinguish `x?: T` from `x: T | undefined`, and say which one a caller may omit",
        "Chain with `?.` and know that a short-circuited chain is always `undefined`",
        "Choose `??` over `||`, and say exactly which values the difference matters for",
        "Say what `!` claims, when it is earned, and what to write instead when it is not",
        "Explain why `catch (e)` is `unknown`, and narrow it safely",
        "Write a custom Error subclass with an extra field, and narrow to it with instanceof",
        "Return failure with a `Result<T>` instead of throwing, and say when each is right",
        "Say why `JSON.parse` returns `any` and what that costs downstream",
        "Replace an `any` from parsed JSON with `unknown` plus a real check",
        "Write a type guard that validates field by field and names the field that failed",
    ],
    why="This is the boundary week. Everything inside your program is as well typed as you made it; everything arriving from outside — a file, a request, a form, another team's API — is `unknown` at best and `any` at worst. The difference between a codebase that holds up and one that does not is whether it checks at that boundary or asserts past it.",
    est_minutes=640,
    glossary=[
        _gloss("undefined", "The absence you did not ask for: unassigned, missing member, missing argument, no return."),
        _gloss("null", "The absence you chose: an intentional empty, a JSON null, a not-found result."),
        _gloss("strictNullChecks", "The strict-mode rule that makes null and undefined their own types rather than members of every type."),
        _gloss("optional member (x?: T)", "The KEY may be absent. `{}` satisfies it."),
        _gloss("T | undefined", "The key must be present; its value may be undefined (TS2741 if omitted)."),
        _gloss("optional chaining (?.)", "`a?.b` is undefined when a is null or undefined, and short-circuits the rest of the chain."),
        _gloss("?.() and ?.[]", "Optional call and optional index — the same short-circuit for a method or a lookup."),
        _gloss("nullish coalescing (??)", "`a ?? b` uses b only when a is null or undefined — not when it is 0, \"\" or false."),
        _gloss("??=", "Assign only if the target is null or undefined."),
        _gloss("|| (the trap)", "Falls back on every falsy value, so it eats 0, \"\" and false."),
        _gloss("non-null assertion (!)", "A claim that a value is not null or undefined. Checked by nobody."),
        _gloss("earned assertion", "A `!` with a guard directly above it that makes the claim true."),
        _gloss("NonNullable<T>", "The utility type that removes null and undefined from a union."),
        _gloss("useUnknownInCatchVariables", "The strict-mode rule that types a caught value `unknown` rather than `any`."),
        _gloss("optional catch binding", "`catch { … }` — legal when you do not need the value."),
        _gloss("finally", "Runs whether or not something was thrown. For cleanup, not for handling."),
        _gloss("Error subclass", "`class ParseError extends Error` — narrowed with instanceof, and may carry extra fields."),
        _gloss("rethrow", "Catching, deciding you cannot handle it, and throwing it on unchanged."),
        _gloss("Result<T, E>", "A discriminated union carrying either a value or an error, returned rather than thrown."),
        _gloss("expected failure", "A failure that is part of the contract — bad input, not found. Return it."),
        _gloss("unexpected failure", "A bug or an unrecoverable condition. Throw it."),
        _gloss("any", "Switches checking off for everything downstream. What JSON.parse returns."),
        _gloss("unknown", "Accepts anything and permits nothing until narrowed. What JSON.parse SHOULD return."),
        _gloss("type guard", "`function isEntry(v: unknown): v is Entry` — a runtime check the compiler trusts."),
        _gloss("parse, don't validate", "Turn untrusted input into a trusted TYPE at one boundary, rather than re-checking everywhere."),
    ],
    cheatsheet="""
```ts
// ---- two absences --------------------------------------------------------
function find(id: string): Entry | null { … }      // null = deliberately none
interface Row { tag?: string; }                     // undefined = key may be absent
if (v == null) { … }                                // loose == catches BOTH (the one good use)

// ---- optional member vs | undefined -------------------------------------
interface A { x?: number; }             // { } is fine
interface B { x: number | undefined; }  // { } is TS2741 — the key is required

// ---- chaining and defaulting --------------------------------------------
const t = row?.meta?.tag;          // string | undefined — never null
const n = fmt.render?.(3);         // optional CALL
const f = list?.[0];               // optional INDEX
const w = width ?? 80;             // only null/undefined fall back
const bad = width || 80;           // ...this also eats 0. Almost always a bug.
opts.retries ??= 3;                // assign only if absent

// ---- the assertion, earned and not -------------------------------------
if (xs.length > 0) { xs[0]!.toFixed(2); }        // ✅ the guard makes it true
xs[0]!.toFixed(2);                                // ❌ a wish
const first = xs[0] ?? 0;                         // better: no claim needed
function must<T>(v: T | undefined, what: string): T {   // better still
  if (v === undefined) throw new Error(`missing ${what}`);
  return v;
}

// ---- catch is unknown ---------------------------------------------------
try { risky(); }
catch (err) {
  // err.message          // ❌ TS18046: 'err' is of type 'unknown'
  console.log(err instanceof Error ? err.message : String(err));
}
finally { /* cleanup, always */ }
catch { /* no binding needed if unused */ }

// ---- custom errors ------------------------------------------------------
class ParseError extends Error {
  readonly line: number;
  constructor(message: string, line: number) {
    super(message);              // FIRST (week 11)
    this.name = "ParseError";
    this.line = line;
  }
}
if (err instanceof ParseError) { err.line; }      // narrowed, extra field available

// ---- Result: return failure instead of throwing ------------------------
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
const r = parseAmount("x");
console.log(r.ok ? r.value.toFixed(2) : r.error);   // must narrow on .ok first

// ---- the JSON boundary --------------------------------------------------
const loose = JSON.parse(text);            // any — checking is OFF from here on
const raw: unknown = JSON.parse(text);     // ✅ admit you know nothing
const lie = JSON.parse(text) as Entry;     // ❌ a claim nobody checked

function isEntry(v: unknown): v is Entry {
  if (typeof v !== "object" || v === null) return false;
  const o = v as Record<string, unknown>;          // the ONE earned assertion
  return typeof o.desc === "string" && typeof o.cents === "number";
}
```
""",
    self_check=[
        "Can you say where `undefined` comes from, and where `null` comes from?",
        "Can you say what `v == null` checks, and why it is the one defensible use of `==`?",
        "Can you say which of `x?: number` and `x: number | undefined` lets a caller write `{}`?",
        "Can you say what `a?.b?.c` evaluates to when `a` is null — and why it is not null?",
        "Can you name the three values `||` gets wrong and `??` gets right?",
        "Can you say what `!` actually checks?",
        "Can you write a guard that makes a `!` unnecessary, and a helper that throws instead?",
        "Can you say why `catch (e)` gives `unknown`, and write the two-branch narrowing for it?",
        "Can you write an Error subclass with an extra field and narrow to it?",
        "Can you say when to return a `Result` and when to throw?",
        "Can you say what `JSON.parse` returns and what that does to every line after it?",
        "Can you write a type guard for an object with two fields, without using `any`?",
        "Can you say why validating once at the boundary beats checking everywhere?",
    ],
    review=[
        _q("`undefined` typically means…",
           ["a deliberate empty", "the absence you did not ask for — unassigned, missing, no return",
            "an error", "zero"], 1,
           "null is the deliberate one."),
        _q("`v == null` (loose) checks…",
           ["only null", "null AND undefined", "only undefined", "everything falsy"], 1,
           "The one defensible use of loose equality."),
        _q("`interface A { x?: number }` — is `const a: A = {}` legal?",
           ["no", "yes — the key may be absent", "only under strict", "only with undefined"], 1,
           "That is what the `?` means."),
        _q("`interface B { x: number | undefined }` — is `const b: B = {}` legal?",
           ["yes", "no — TS2741, the key is required", "only with strict", "same as A"], 1,
           "The value may be undefined; the key may not be missing."),
        _q("`a?.b` where a is null evaluates to…",
           ["null", "undefined", "an error", "b"], 1,
           "A short-circuited chain is always undefined, never null."),
        _q("`width || 80` where width is 0 gives…",
           ["0", "80 — which is almost always a bug", "undefined", "an error"], 1,
           "`||` falls back on every falsy value."),
        _q("`width ?? 80` where width is 0 gives…",
           ["80", "0", "undefined", "an error"], 1,
           "`??` only cares about null and undefined."),
        _q("`xs[0]!` claims…",
           ["that xs is not empty, and is checked", "that the value is not null/undefined, and is checked by nobody",
            "the array is readonly", "nothing"], 1,
           "It is a claim, not a check."),
        _q("A `!` is earned when…",
           ["it is on an array", "a guard directly above it makes the claim true", "never",
            "the type is number"], 1,
           "Otherwise it is a wish."),
        _q("`catch (err)` types err as…",
           ["Error", "unknown, under strict", "any", "never"], 1,
           "useUnknownInCatchVariables — anything can be thrown."),
        _q("Reading `err.message` straight out of a catch gives…",
           ["the message", "TS18046: 'err' is of type 'unknown'", "undefined", "any"], 1,
           "Narrow with instanceof Error first."),
        _q("In a derived Error's constructor, `super(message)` must come…",
           ["last", "before any use of `this`", "anywhere", "nowhere"], 1,
           "Week 11's rule, unchanged."),
        _q("A `Result<T>` is best for…",
           ["bugs", "expected failures that are part of the contract — bad input, not found",
            "everything", "nothing"], 1,
           "Throw for the unexpected."),
        _q("`const r = parse(s); r.value` without narrowing gives…",
           ["the value", "TS2339 — value does not exist on the failure member", "undefined",
            "any"], 1,
           "Check `r.ok` first; that is the point of the discriminant."),
        _q("`JSON.parse` returns…",
           ["unknown", "any — so checking is off for everything downstream", "object",
            "string"], 1,
           "The one place the type system is silently switched off."),
        _q("`JSON.parse(text) as Entry` is…",
           ["a runtime check", "a claim nobody checked", "safe", "the same as a guard"], 1,
           "Week 12 told you what `as` is worth."),
        _q("The honest first move with parsed JSON is…",
           ["as Entry", "annotate it `unknown` and narrow", "any", "a cast to object"], 1,
           "Admit you know nothing, then check."),
        _q("Inside a type guard, `v as Record<string, unknown>` is acceptable because…",
           ["assertions are fine", "a typeof and null check directly above it make the claim true",
            "it is unknown", "guards are exempt"], 1,
           "One earned assertion, in one place."),
        _q("\"Parse, don't validate\" means…",
           ["never check", "turn untrusted input into a trusted TYPE once, at the boundary",
            "validate at every use", "use any"], 1,
           "Then the rest of the program needs no checks at all."),
    ],
    milestone="Budget Buddy can finally read a file it did not write. A JSON ledger goes through one boundary function that either hands back a fully typed `readonly Entry[]` or names the exact field that was wrong — `entries[0].cents must be a number`. Nothing gets in unchecked, and nothing downstream needs to check again.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w15-absences", "`null` and `undefined`",
            "Two ways to say nothing, and where each comes from.",
            """
JavaScript has two empties. TypeScript keeps them apart, because
`strictNullChecks` has been on since week 1 — which is why `string` has never
included `null` in this course, and why every absence has had to be handled.

## Where each one comes from

**`undefined` — the absence you did not ask for:**

```ts
let x: number | undefined;         // declared, never assigned
const row: { tag?: string } = {};  // row.tag — the member is absent
function f(a: number, b?: number) { }   // b, when the caller omits it
function g(): void { }             // what g "returns"
const first = [1, 2][5];           // an index past the end
```

**`null` — the absence somebody chose:**

```ts
function find(id: string): Entry | null {   // "I looked; there is none"
  return null;
}
JSON.parse('{"tag":null}').tag;             // JSON has null and not undefined
document.getElementById("nope");            // most DOM APIs return null
```

The distinction that survives contact with real code: **`undefined` happens,
`null` is stated.**

## Checking for both

```ts
function label(v: string | null | undefined): string {
  if (v == null) {          // loose == — catches null AND undefined
    return "-";
  }
  return v.toUpperCase();   // narrowed to string
}
```

`v == null` is the one place loose equality earns its keep: `null == undefined`
is `true`, so a single test covers both, and it is deliberate rather than
accidental. Every other `==` in your code should be `===`. Many linters allow
exactly this exception.

The strict alternative spells it out:

```ts
if (v === null || v === undefined) { … }
```

Both narrow correctly. Use whichever your codebase prefers, consistently.

## `typeof null` is `"object"`

A JavaScript wart worth knowing, because it breaks the obvious guard:

```ts
function isObject(v: unknown): boolean {
  return typeof v === "object";       // TRUE for null. Not what you meant.
}
```

The correct shape, which lesson 9 uses constantly:

```ts
return typeof v === "object" && v !== null;
```

## Pick a convention

For code you write, prefer `undefined`. It is what the language produces by
itself, it works with `?`, with optional parameters and with defaults, and it
means you have one absence rather than two.

Accept `null` where it arrives from outside — JSON, a database driver, the DOM —
and normalise it at the boundary:

```ts
const tag = raw.tag ?? undefined;
```

The type to reach for when a union has collected both is `NonNullable<T>`, the
utility from week 14's family:

```ts
type Maybe = string | null | undefined;
type Sure = NonNullable<Maybe>;      // string
```

> ⚠️ **Common mistakes:** using `typeof v === "object"` and being surprised by
> `null`; mixing both absences in your own return types so callers must handle
> two; and `=== undefined` on a value that is actually `null`.
""",
            warmup=[
                _q("A declared-but-unassigned variable is…",
                   ["null", "undefined", "0", "an error"], 1,
                   "The absence you did not ask for."),
                _q("`JSON.parse('{\"tag\":null}').tag` is…",
                   ["undefined", "null", "\"null\"", "an error"], 1,
                   "JSON has null and no undefined at all."),
                _q("`v == null` catches…",
                   ["only null", "null and undefined", "everything falsy", "only undefined"], 1,
                   "The one defensible loose equality."),
                _q("`typeof null` is…",
                   ['"null"', '"object"', '"undefined"', "an error"], 1,
                   "Which is why an object guard needs `&& v !== null`."),
            ],
            exercises=[
                _ex("tscourse-w15-ab-1", "A deliberate absence",
                    "Return null when there is no match, and handle it at the call site.",
                    'interface Entry {\n  readonly desc: string;\n}\n'
                    'const entries: readonly Entry[] = [{ desc: "coffee" }];\n'
                    'function find(desc: string): Entry | null {\n'
                    '  return entries.find((e) => e.desc === desc) ?? null;\n}\n'
                    'console.log(find("coffee")?.desc ?? "none");\n'
                    'console.log(find("rent")?.desc ?? "none");\n',
                    'return entries.find((e) => e.desc === desc) ?? null;',
                    [("", "coffee\nnone")],
                    hints=["`find` already gives you `Entry | undefined` — turn that into the declared `Entry | null`.",
                           "Write return entries.find((e) => e.desc === desc) ?? null;"],
                    difficulty="Medium"),
                _ex("tscourse-w15-ab-2", "Catch both at once",
                    "Test for null and undefined together, so the narrowed value can be uppercased.",
                    'function label(v: string | null | undefined): string {\n'
                    '  if (v == null) {\n    return "-";\n  }\n'
                    '  return v.toUpperCase();\n}\n'
                    'console.log(`${label("food")} ${label(null)} ${label(undefined)}`);\n',
                    'if (v == null) {', [("", "FOOD - -")],
                    hints=["One loose comparison covers both absences.",
                           "Write if (v == null) {"],
                    difficulty="Medium"),
                _ex("tscourse-w15-ab-3", "An object guard that is not fooled",
                    "Write the check so null does not count as an object.",
                    'function isObject(v: unknown): boolean {\n'
                    '  return typeof v === "object" && v !== null;\n}\n'
                    'console.log(`${isObject({})} ${isObject(null)} ${isObject("x")}`);\n',
                    'return typeof v === "object" && v !== null;',
                    [("", "true false true".replace("true false true", "true false false"))],
                    hints=['`typeof null` is "object", so the typeof test alone is not enough.',
                           "Add an explicit null comparison."],
                    difficulty="Medium"),
                _ex("tscourse-w15-ab-4", "Normalise at the boundary",
                    "Turn an incoming null into undefined, so the rest of the program has one absence to handle.",
                    'interface Raw {\n  readonly tag: string | null;\n}\n'
                    'function normalise(r: Raw): string | undefined {\n'
                    '  return r.tag ?? undefined;\n}\n'
                    'console.log(`${normalise({ tag: "food" }) ?? "-"} ${normalise({ tag: null }) ?? "-"}`);\n',
                    'return r.tag ?? undefined;', [("", "food -")],
                    hints=["`??` fires on null, so the fallback is what the caller sees.",
                           "Write return r.tag ?? undefined;"],
                    difficulty="Medium"),
                _ex("tscourse-w15-ab-5", "Remove both from a union",
                    "Derive the certain type from the maybe type with week 14's utility.",
                    'type Maybe = string | null | undefined;\n'
                    'type Sure = NonNullable<Maybe>;\n'
                    'function shout(v: Sure): string {\n'
                    '  return v.toUpperCase();\n}\n'
                    'console.log(shout("food"));\n',
                    'type Sure = NonNullable<Maybe>;', [("", "FOOD")],
                    hints=["One utility type, taking the union.",
                           "Write type Sure = NonNullable<Maybe>;"]),
                _predict("tscourse-w15-ab-p1", "What find really gives you",
                         'interface Entry {\n  readonly desc: string;\n}\n'
                         'const entries: readonly Entry[] = [{ desc: "coffee" }];\n'
                         'const got = entries.find((e) => e.desc === "rent");\n',
                         "got", "Entry | undefined",
                         why="`find` may find nothing, and the standard library is explicit about "
                             "which absence it uses.",
                         hints=["The array's element type, plus one of the two absences.",
                                "The standard library uses undefined, not null.",
                                "Write Entry | undefined."]),
                _diagnose("tscourse-w15-ab-d1", "The deliberate empty",
                          "TS18047: 'found' is possibly 'null'.",
                          'interface Entry {\n  readonly desc: string;\n}\n'
                          'const entries: readonly Entry[] = [{ desc: "coffee" }];\n'
                          'function find(desc: string): Entry | null {\n'
                          '  return entries.find((e) => e.desc === desc) ?? null;\n}\n'
                          'const found = find("rent");\n'
                          'console.log(found.desc);\n',
                          'interface Entry {\n  readonly desc: string;\n}\n'
                          'const entries: readonly Entry[] = [{ desc: "coffee" }];\n'
                          'function find(desc: string): Entry | null {\n'
                          '  return entries.find((e) => e.desc === desc) ?? null;\n}\n'
                          'const found = find("rent");\n'
                          'console.log(found?.desc ?? "none");\n',
                          [("", "none")],
                          hints=["The function's own signature says it may return null, and this call does.",
                                 "Chain past the absence and supply a fallback.",
                                 'Write found?.desc ?? "none".'],
                          difficulty="Medium"),
                _fix("tscourse-w15-ab-fix1", "Fix the label that printed the absence",
                     "`String(v)` happily turns null into the text `null`, so this prints `[null]` instead of `[-]`.",
                     'function label(v: string | null): string {\n'
                     '  return `[${String(v)}]`;\n}\n'
                     'console.log(label("food"));\n'
                     'console.log(label(null));\n',
                     'function label(v: string | null): string {\n'
                     '  return `[${v ?? "-"}]`;\n}\n'
                     'console.log(label("food"));\n'
                     'console.log(label(null));\n',
                     [("", "[food]\n[-]")],
                     hints=["`String(null)` is the four-character string \"null\" — a perfectly valid string, so nothing complained.",
                            "Supply the fallback before the value reaches the template.",
                            'Write `[${v ?? "-"}]`.'],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("For your own code, prefer…",
                   ["null", "undefined — it is what the language produces and works with `?`",
                    "both", "neither"], 1,
                   "One absence is easier than two."),
                _q("`NonNullable<T>` removes…",
                   ["undefined only", "null and undefined", "null only", "falsy values"], 1,
                   "The week 14 utility for exactly this."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w15-optional", "Optional members and `| undefined`",
            "They look the same and they are not.",
            """
Two declarations that people treat as interchangeable:

```ts
interface A { x?: number; }
interface B { x: number | undefined; }
```

Reading `a.x` and `b.x` both give `number | undefined`. **Building** them is
where they differ:

```ts
const a: A = {};      // ✅ the key may be absent
const b: B = {};
// ❌ TS2741: Property 'x' is missing in type '{}'
//            but required in type 'B'.

const b2: B = { x: undefined };   // ✅ the key is there, holding undefined
```

`?` makes the **key** optional. `| undefined` makes the **value** possibly
undefined, and still demands the key.

## Which to use

**`x?: T` almost always.** It is what a caller expects, it works with object
spreads, and it is the shape every options object in the ecosystem uses.

**`x: T | undefined` when the key being present is meaningful.** The classic case
is distinguishing "not supplied" from "explicitly cleared":

```ts
interface Patch {
  tag: string | undefined;    // present-and-undefined means "remove the tag"
}
```

With `tag?: string` you cannot tell those apart, because `{}` and
`{ tag: undefined }` are the same value as far as the type is concerned. Making
the key required forces the caller to be explicit. It is a rare need — but when
you need it, `?` cannot express it.

## Optional parameters

The same `?`, with one extra rule: optional parameters must come last.

```ts
function fmt(desc: string, width?: number): string {
  return desc.padEnd(width ?? 10);
}
fmt("coffee");        // width is undefined
fmt("coffee", 20);
```

A **default** is usually better, because the body then has no absence to handle
at all:

```ts
function fmt(desc: string, width: number = 10): string {
  return desc.padEnd(width);      // width is `number`, not `number | undefined`
}
```

Note that a defaulted parameter is still optional to the caller — you get the
convenience without the union.

## One flag worth knowing about

By default, `x?: number` also *accepts* an explicit `undefined`:

```ts
const a: A = { x: undefined };    // ✅ allowed
```

The compiler flag `exactOptionalPropertyTypes` makes that an error, separating
"absent" from "present but undefined" for optional members too. **It is not on in
this course**, and it is off by default in most projects — but if a codebase
turns it on, that is what changed.

> ⚠️ **Common mistakes:** using `x: T | undefined` when you meant `x?: T`, and
> making every caller write `{ x: undefined }`; putting an optional parameter
> before a required one; and reaching for `?` when you specifically needed to
> tell "absent" from "cleared".
""",
            warmup=[
                _q("`interface A { x?: number }` — `const a: A = {}` is…",
                   ["TS2741", "legal", "a warning", "only legal under strict"], 1,
                   "The key may be absent."),
                _q("`interface B { x: number | undefined }` — `const b: B = {}` is…",
                   ["legal", "TS2741 — the key is required", "a warning", "the same as A"], 1,
                   "The value may be undefined; the key may not be missing."),
                _q("Reading `a.x` and `b.x` gives…",
                   ["different types", "the same type: number | undefined", "number", "never"], 1,
                   "They differ in construction, not in reading."),
                _q("A defaulted parameter `width: number = 10` is typed inside the body as…",
                   ["number | undefined", "number", "never", "unknown"], 1,
                   "Which is why a default beats an optional."),
            ],
            exercises=[
                _ex("tscourse-w15-op-1", "An optional key",
                    "Declare `tag` so an object without it is still valid.",
                    'interface Row {\n  readonly desc: string;\n  readonly tag?: string;\n}\n'
                    'const a: Row = { desc: "coffee", tag: "food" };\n'
                    'const b: Row = { desc: "rent" };\n'
                    'console.log(`${a.tag ?? "-"} ${b.tag ?? "-"}`);\n',
                    'readonly tag?: string;', [("", "food -")],
                    hints=["A question mark after the member name.",
                           "Write readonly tag?: string;"]),
                _ex("tscourse-w15-op-2", "A key that must be stated",
                    "Declare `tag` so the key is required but its value may be undefined — so a caller has to say \"cleared\" out loud.",
                    'interface Patch {\n  readonly tag: string | undefined;\n}\n'
                    'function describe(p: Patch): string {\n'
                    '  return p.tag === undefined ? "clear the tag" : `set tag to ${p.tag}`;\n}\n'
                    'console.log(describe({ tag: "food" }));\n'
                    'console.log(describe({ tag: undefined }));\n',
                    'readonly tag: string | undefined;',
                    [("", "set tag to food\nclear the tag")],
                    hints=["No question mark — a union with undefined instead.",
                           "That is what forces the caller to write `{ tag: undefined }` deliberately.",
                           "Write readonly tag: string | undefined;"],
                    difficulty="Medium"),
                _ex("tscourse-w15-op-3", "A default beats an optional",
                    "Give the width a default, so the body has no absence to handle.",
                    'function fmt(desc: string, width: number = 10): string {\n'
                    '  return `[${desc.padEnd(width)}]`;\n}\n'
                    'console.log(fmt("coffee"));\n'
                    'console.log(fmt("coffee", 3));\n',
                    'width: number = 10', [("", "[coffee    ]\n[coffee]")],
                    hints=["A default value makes the parameter optional to callers AND non-optional inside.",
                           "Write width: number = 10"],
                    difficulty="Medium"),
                _ex("tscourse-w15-op-4", "Optional, then defaulted in the body",
                    "Supply the fallback where the optional parameter is used.",
                    'function fmt(desc: string, width?: number): string {\n'
                    '  return `[${desc.padEnd(width ?? 10)}]`;\n}\n'
                    'console.log(fmt("coffee"));\n'
                    'console.log(fmt("coffee", 3));\n',
                    'width ?? 10', [("", "[coffee    ]\n[coffee]")],
                    hints=["The parameter is `number | undefined` here, and padEnd needs a number.",
                           "Write width ?? 10"]),
                _predict("tscourse-w15-op-p1", "Reading an optional member",
                         'interface Row {\n  readonly desc: string;\n  readonly tag?: string;\n}\n'
                         'const r: Row = { desc: "coffee", tag: "food" };\n'
                         'const got = r.tag;\n',
                         "got", "string | undefined",
                         why="The value plainly has a tag. The declaration is what the read goes "
                             "through.",
                         hints=["An optional member might not be there, as far as the type knows.",
                                "Write string | undefined."]),
                _diagnose("tscourse-w15-op-d1", "The key that cannot be omitted",
                          "TS2345: Argument of type '{ desc: string; }' is not assignable to parameter of type 'Patch'. Property 'tag' is missing in type '{ desc: string; }' but required in type 'Patch'.",
                          'interface Patch {\n  readonly desc: string;\n  readonly tag: string | undefined;\n}\n'
                          'function describe(p: Patch): string {\n'
                          '  return `${p.desc}/${p.tag ?? "none"}`;\n}\n'
                          'console.log(describe({ desc: "coffee" }));\n',
                          'interface Patch {\n  readonly desc: string;\n  readonly tag: string | undefined;\n}\n'
                          'function describe(p: Patch): string {\n'
                          '  return `${p.desc}/${p.tag ?? "none"}`;\n}\n'
                          'console.log(describe({ desc: "coffee", tag: undefined }));\n',
                          [("", "coffee/none")],
                          hints=["`| undefined` makes the VALUE optional, not the key.",
                                 "Do not change the interface — the required key is deliberate here.",
                                 "State the absence explicitly: tag: undefined."],
                          difficulty="Medium"),
                _fix("tscourse-w15-op-fix1", "Fix the optional that should have been a default",
                     "`width` is optional and the body forgot to default it, so `padEnd(undefined)` pads to nothing — this prints `[coffee]` instead of `[coffee    ]` on the first line.",
                     'function fmt(desc: string, width?: number): string {\n'
                     '  return `[${desc.padEnd(width as number)}]`;\n}\n'
                     'console.log(fmt("coffee"));\n'
                     'console.log(fmt("coffee", 3));\n',
                     'function fmt(desc: string, width: number = 10): string {\n'
                     '  return `[${desc.padEnd(width)}]`;\n}\n'
                     'console.log(fmt("coffee"));\n'
                     'console.log(fmt("coffee", 3));\n',
                     [("", "[coffee    ]\n[coffee]")],
                     hints=["`width as number` is an assertion, and it was false — the value really was undefined.",
                            "Give the parameter a default of 10 instead of asserting.",
                            "Then the body needs no assertion and no `??` at all."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`x: T | undefined` is worth the friction when…",
                   ["always", "you must tell \"not supplied\" from \"explicitly cleared\"",
                    "never", "T is a number"], 1,
                   "A rare need that `?` cannot express."),
                _q("`exactOptionalPropertyTypes` …",
                   ["is on in this course", "is off here, and separates absent from present-and-undefined",
                    "is part of strict", "does nothing"], 1,
                   "Worth recognising if a codebase enables it."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w15-chain", "`?.` and `??`",
            "The whole rule for two operators you already use.",
            """
Week 7 introduced `?.` and week 6 introduced `??` the day
`noUncheckedIndexedAccess` turned on. Here is everything they do.

## Optional chaining short-circuits the whole chain

```ts
const tag = row?.meta?.tag;
```

If `row` is null or undefined, evaluation stops **immediately** and the result is
`undefined`. `meta` is never touched. That matters: `row?.meta.tag` (only one
`?.`) still crashes if `meta` is absent, because you only guarded `row`.

**The result is always `undefined`, never `null`**, even when the thing that was
null was `null`:

```ts
const row: { meta?: { tag: string } } | null = null;
const tag = row?.meta?.tag;      // undefined — not null
```

So a chain's type is `T | undefined`, and one `??` at the end handles every
absence in it.

## Optional call and optional index

```ts
const rendered = fmt.render?.(3);     // call it only if it is there
const first = list?.[0];              // index only if list is there
```

`fmt.render?.(3)` is not `fmt.render?(3)` — the `?.` comes before the
parentheses. Same for `?.[`. This is how you call a callback that may not have
been supplied, without an `if`.

## `??` versus `||` — the one that bites

```ts
function widthOr(n: number | undefined): number {
  return n ?? 80;
}
function widthOrBad(n: number | undefined): number {
  return n || 80;
}

widthOr(0);       // 0    ✅
widthOrBad(0);    // 80   ❌
```

`??` falls back only on **null and undefined**. `||` falls back on every **falsy**
value, and that list includes the three that are usually legitimate data:

* `0` — a width, a count, a price, an index
* `""` — an empty description, a cleared field
* `false` — a flag that is deliberately off

That is a real bug and a common one: `const retries = opts.retries || 3` cannot
express "zero retries".

Use `??` unless you specifically want falsy-means-absent, which is rare enough
that it deserves a comment when you do.

## `??=`

Assign only if the target is currently null or undefined:

```ts
let width: number | undefined;
width ??= 80;         // width is now 80
width ??= 100;        // unchanged — it is no longer nullish
```

There are `||=` and `&&=` too, with the same falsy caveat as `||`.

## What chaining does not do

`?.` guards **absence**, not **errors**. `a?.b()` will happily throw whatever
`b()` throws. And it does not make a value non-optional for the *next* statement:

```ts
if (row?.meta !== undefined) {
  row.meta.tag;       // ✅ this narrows, because the chain was the condition
}
```

That works, but a plain guard usually reads better.

> ⚠️ **Common mistakes:** one `?.` in a chain that needed two; `||` where `??`
> was meant; and reaching for `?.` to paper over a value that should never have
> been optional in the first place.
""",
            warmup=[
                _q("`row?.meta?.tag` where row is null evaluates to…",
                   ["null", "undefined", "an error", "{}"], 1,
                   "A short-circuited chain is always undefined."),
                _q("`row?.meta.tag` where meta is absent…",
                   ["is undefined", "still crashes — only row was guarded", "is null",
                    "is a type error"], 1,
                   "Each link needs its own `?.`."),
                _q("`n || 80` where n is 0 gives…",
                   ["0", "80", "undefined", "an error"], 1,
                   "`||` eats every falsy value."),
                _q("`width ??= 80` assigns when width is…",
                   ["falsy", "null or undefined", "zero", "always"], 1,
                   "Same rule as `??`."),
            ],
            exercises=[
                _ex("tscourse-w15-ch-1", "Guard every link",
                    "Reach the tag safely when either level may be absent.",
                    'interface Row {\n  readonly meta?: { readonly tag?: string };\n}\n'
                    'function tagOf(row: Row | null): string {\n'
                    '  return row?.meta?.tag ?? "-";\n}\n'
                    'console.log(tagOf({ meta: { tag: "food" } }));\n'
                    'console.log(tagOf({ meta: {} }));\n'
                    'console.log(tagOf({}));\n'
                    'console.log(tagOf(null));\n',
                    'return row?.meta?.tag ?? "-";',
                    [("", "food\n-\n-\n-")],
                    hints=["Three things may be absent, so two `?.` and one `??`.",
                           'Write return row?.meta?.tag ?? "-";'],
                    difficulty="Medium"),
                _ex("tscourse-w15-ch-2", "Call it only if it is there",
                    "Invoke the optional renderer, falling back when it was not supplied.",
                    'interface Fmt {\n  readonly render?: (n: number) => string;\n}\n'
                    'function show(f: Fmt, n: number): string {\n'
                    '  return f.render?.(n) ?? String(n);\n}\n'
                    'console.log(show({ render: (n: number): string => `#${n}` }, 3));\n'
                    'console.log(show({}, 3));\n',
                    'return f.render?.(n) ?? String(n);',
                    [("", "#3\n3")],
                    hints=["The `?.` goes before the parentheses: render?.(n).",
                           "Then a `??` for the case where it was absent."],
                    difficulty="Medium"),
                _ex("tscourse-w15-ch-3", "Index only if it is there",
                    "Read the first element of a list that may itself be absent.",
                    'function firstOf(list: readonly string[] | undefined): string {\n'
                    '  return list?.[0] ?? "-";\n}\n'
                    'console.log(firstOf(["food", "home"]));\n'
                    'console.log(firstOf([]));\n'
                    'console.log(firstOf(undefined));\n',
                    'return list?.[0] ?? "-";', [("", "food\n-\n-")],
                    hints=["The optional index is `?.[0]`.",
                           "The empty-array case is handled by the same `??`, because the index gives undefined."],
                    difficulty="Medium"),
                _ex("tscourse-w15-ch-4", "Zero is data",
                    "Fall back only on a real absence, so a width of 0 survives.",
                    'function widthOr(n: number | undefined): number {\n'
                    '  return n ?? 80;\n}\n'
                    'console.log(`${widthOr(20)} ${widthOr(0)} ${widthOr(undefined)}`);\n',
                    'return n ?? 80;', [("", "20 0 80")],
                    hints=["`||` would turn the 0 into 80, which the expected output forbids.",
                           "Write return n ?? 80;"]),
                _ex("tscourse-w15-ch-5", "Assign only if absent",
                    "Set the default in place, without overwriting a value that is already there.",
                    'function resolve(given: number | undefined): number {\n'
                    '  let width = given;\n'
                    '  width ??= 80;\n'
                    '  return width;\n}\n'
                    'console.log(`${resolve(20)} ${resolve(0)} ${resolve(undefined)}`);\n',
                    'width ??= 80;', [("", "20 0 80")],
                    hints=["The nullish assignment operator.",
                           "Write width ??= 80;"],
                    difficulty="Medium"),
                _predict("tscourse-w15-ch-p1", "The type of a chain",
                         'interface Row {\n  readonly meta?: { readonly tag: string };\n}\n'
                         'function load(): Row | null {\n  return null;\n}\n'
                         'const row = load();\n'
                         'const got = row?.meta?.tag;\n',
                         "got", "string | undefined",
                         why="Note which absence a short-circuited chain produces — `load` "
                             "returns null, after all.",
                         hints=["The chain's value when it short-circuits is always undefined, never null.",
                                "So the union is the member's type plus that one absence.",
                                "Write string | undefined."],
                         difficulty="Medium"),
                _diagnose("tscourse-w15-ch-d1", "The link that was not guarded",
                          "TS18048: 'row.meta' is possibly 'undefined'.",
                          'interface Row {\n  readonly meta?: { readonly tag: string };\n}\n'
                          'function tagOf(row: Row): string {\n'
                          '  return row.meta.tag;\n}\n'
                          'console.log(tagOf({ meta: { tag: "food" } }));\n'
                          'console.log(tagOf({}));\n',
                          'interface Row {\n  readonly meta?: { readonly tag: string };\n}\n'
                          'function tagOf(row: Row): string {\n'
                          '  return row.meta?.tag ?? "-";\n}\n'
                          'console.log(tagOf({ meta: { tag: "food" } }));\n'
                          'console.log(tagOf({}));\n',
                          [("", "food\n-")],
                          hints=["The second call proves the compiler right — that object has no meta at all.",
                                 "Guard the optional link and supply a fallback.",
                                 'Write row.meta?.tag ?? "-".'],
                          difficulty="Medium"),
                _fix("tscourse-w15-ch-fix1", "Fix the fallback that ate a zero",
                     "`||` treats 0 as absent, so a deliberate width of 0 becomes 80 — this prints `20 80 80` instead of `20 0 80`.",
                     'function widthOr(n: number | undefined): number {\n'
                     '  return n || 80;\n}\n'
                     'console.log(`${widthOr(20)} ${widthOr(0)} ${widthOr(undefined)}`);\n',
                     'function widthOr(n: number | undefined): number {\n'
                     '  return n ?? 80;\n}\n'
                     'console.log(`${widthOr(20)} ${widthOr(0)} ${widthOr(undefined)}`);\n',
                     [("", "20 0 80")],
                     hints=["Both operators have the same type, so nothing was reported.",
                            "`||` falls back on every falsy value: 0, \"\" and false included.",
                            "Use the operator that only cares about null and undefined."]),
            ],
            quiz=[
                _q("`?.` guards…",
                   ["errors", "absence only — a thrown error still propagates", "everything",
                    "type errors"], 1,
                   "It is not a try/catch."),
                _q("`opts.retries || 3` cannot express…",
                   ["three retries", "zero retries", "undefined", "a default"], 1,
                   "Which is exactly the bug."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w15-nonnull", "The non-null assertion, and when it is earned",
            "`!` is a promise, not a check.",
            """
You have written `!` since week 6, because `noUncheckedIndexedAccess` types
`xs[0]` as `T | undefined` and something had to give. Here is what it actually
means.

```ts
const first = xs[0]!;
```

`!` removes `null` and `undefined` from the type. It generates **no code** and
performs **no check**. It is you telling the compiler "I know something you
don't", and if you are wrong nothing catches it — the program simply carries a
value the types say cannot exist.

```ts
const xs: readonly number[] = [];
const first = xs[0]!;          // typed number
console.log(first.toFixed(2)); // TypeError at runtime
```

**A note on the two error codes.** Drop the `!` and which error you get depends
on what you indexed:

```ts
xs[0].toFixed(2);         // TS2532: Object is possibly 'undefined'.
row.meta.tag;             // TS18048: 'row.meta' is possibly 'undefined'.
```

An **element access** gives the older, anonymous TS2532, because there is no name
to quote. A **named property path** gives TS18048 and names it. Same rule, two
messages — worth recognising both, because searching for the wrong one wastes a
few minutes.

## When it is earned

**When a guard directly above it makes the claim true:**

```ts
if (xs.length > 0) {
  console.log(xs[0]!.toFixed(2));    // ✅ the guard is the proof
}
```

**When you just built the value:**

```ts
const parts = "coffee 3.25".split(" ");
const desc = parts[0]!;      // ✅ split always yields at least one element
```

The test is simple: **can you say, in one sentence, why this cannot be
undefined?** If yes, the `!` is documentation. If you find yourself saying "it
shouldn't be", it is a wish.

## Three better options

**A default, when there is a sensible one.** No claim needed at all:

```ts
const first = xs[0] ?? 0;
```

**A guard, when the absence is a real case.** The narrowing is free:

```ts
const first = xs[0];
if (first === undefined) {
  return "empty";
}
first.toFixed(2);        // narrowed to number, no ! anywhere
```

**A throwing helper, when absence is a bug you want reported loudly.** This is
the professional answer, and it is a one-liner with week 10's generics:

```ts
function must<T>(v: T | undefined, what: string): T {
  if (v === undefined) {
    throw new Error(`missing ${what}`);
  }
  return v;
}

const first = must(xs[0], "first entry");
```

`must` gives you what `!` gives you — a non-optional value on one line — plus an
error that says what was missing, at the moment it was missing. Compare a
`TypeError: Cannot read properties of undefined` twenty frames away.

## `!` versus `as`

Both override the compiler and neither checks anything. `!` is narrower — it only
removes the two absences — so it is the lesser evil, and it is much easier to
search for. A codebase with a hundred `!`s has a hundred small claims; a codebase
with a hundred `as`es has a hundred arbitrary ones.

Neither belongs in a boundary. Lesson 9 is about what does.

> ⚠️ **Common mistakes:** a `!` whose guard is *near* it rather than above it (an
> `if` in another branch proves nothing); `!` on a value from `JSON.parse` or an
> API, where you genuinely do not know; and `xs[i]!` inside a loop whose bound is
> not `xs.length`.
""",
            warmup=[
                _q("`xs[0]!` performs…",
                   ["a runtime check", "no check at all", "a cast", "a copy"], 1,
                   "It removes null and undefined from the TYPE and nothing else."),
                _q("A `!` is earned when…",
                   ["the value is a number", "a guard directly above it makes the claim true",
                    "you are in a loop", "always"], 1,
                   "One sentence saying why it cannot be undefined."),
                _q("The professional alternative to an unearned `!` is…",
                   ["as any", "a helper that throws a named error", "a comment", "??"], 1,
                   "must(v, what) reports what was missing, where."),
                _q("`!` compared with `as` is…",
                   ["worse", "narrower — it only removes the two absences", "the same",
                    "checked"], 1,
                   "And easier to grep for."),
            ],
            exercises=[
                _ex("tscourse-w15-nn-1", "An earned assertion",
                    "Guard the array first, so the assertion below it is a fact.",
                    'function firstOf(xs: readonly number[]): string {\n'
                    '  if (xs.length > 0) {\n'
                    '    return xs[0]!.toFixed(2);\n  }\n'
                    '  return "empty";\n}\n'
                    'console.log(firstOf([3.5, 1]));\n'
                    'console.log(firstOf([]));\n',
                    'if (xs.length > 0) {', [("", "3.50\nempty")],
                    hints=["The guard is what makes the ! honest.",
                           "Write if (xs.length > 0) {"],
                    difficulty="Medium"),
                _ex("tscourse-w15-nn-2", "No claim needed",
                    "Supply a default instead of asserting.",
                    'function firstOr(xs: readonly number[]): string {\n'
                    '  return (xs[0] ?? 0).toFixed(2);\n}\n'
                    'console.log(firstOr([3.5, 1]));\n'
                    'console.log(firstOr([]));\n',
                    'return (xs[0] ?? 0).toFixed(2);', [("", "3.50\n0.00")],
                    hints=["Default the value before calling a method on it.",
                           "The parentheses matter: default first, then .toFixed."],
                    difficulty="Medium"),
                _ex("tscourse-w15-nn-3", "Guard, then use the narrowing",
                    "Bind the value, test it, and let narrowing do the rest — no assertion anywhere.",
                    'function firstOf(xs: readonly number[]): string {\n'
                    '  const first = xs[0];\n'
                    '  if (first === undefined) {\n    return "empty";\n  }\n'
                    '  return first.toFixed(2);\n}\n'
                    'console.log(firstOf([3.5, 1]));\n'
                    'console.log(firstOf([]));\n',
                    'if (first === undefined) {\n    return "empty";\n  }',
                    [("", "3.50\nempty")],
                    hints=["Return early on the absence, and the compiler narrows what follows.",
                           "Compare with === undefined."],
                    difficulty="Medium"),
                _ex("tscourse-w15-nn-4", "A helper that says what was missing",
                    "Write the generic `must`, so an absence throws a named error instead of being asserted away.",
                    'function must<T>(v: T | undefined, what: string): T {\n'
                    '  if (v === undefined) {\n'
                    '    throw new Error(`missing ${what}`);\n  }\n'
                    '  return v;\n}\n'
                    'const xs: readonly number[] = [3.5];\n'
                    'console.log(must(xs[0], "first entry").toFixed(2));\n'
                    'try {\n  console.log(must(xs[9], "tenth entry").toFixed(2));\n'
                    '} catch (err) {\n'
                    '  console.log(err instanceof Error ? err.message : "?");\n}\n',
                    'if (v === undefined) {\n'
                    '    throw new Error(`missing ${what}`);\n  }',
                    [("", "3.50\nmissing tenth entry")],
                    hints=["Throw when the value is absent, naming what it was.",
                           "The generic then returns T rather than T | undefined.",
                           "Week 10's generics doing real work."],
                    difficulty="Medium"),
                _ex("tscourse-w15-nn-5", "Earned because you just built it",
                    "`split` always yields at least one element, so name the first part without a guard.",
                    'function descOf(line: string): string {\n'
                    '  const parts = line.split(" ");\n'
                    '  return parts[0]!;\n}\n'
                    'console.log(descOf("coffee 3.25"));\n'
                    'console.log(`[${descOf("")}]`);\n',
                    'return parts[0]!;', [("", "coffee\n[]")],
                    hints=["Even splitting the empty string gives a one-element array.",
                           "That is the sentence which earns the assertion."],
                    difficulty="Medium"),
                _diagnose("tscourse-w15-nn-d1", "The index that might find nothing",
                          "TS2532: Object is possibly 'undefined'.",
                          'function firstOf(xs: readonly number[]): string {\n'
                          '  return xs[0].toFixed(2);\n}\n'
                          'console.log(firstOf([3.5]));\n'
                          'console.log(firstOf([]));\n',
                          'function firstOf(xs: readonly number[]): string {\n'
                          '  return (xs[0] ?? 0).toFixed(2);\n}\n'
                          'console.log(firstOf([3.5]));\n'
                          'console.log(firstOf([]));\n',
                          [("", "3.50\n0.00")],
                          hints=["The second call is the empty array, so a `!` here would be a lie.",
                                 "Default the value rather than asserting it.",
                                 "The expected output tells you what the default has to be."],
                          difficulty="Medium"),
                _fix("tscourse-w15-nn-fix1", "Fix the assertion that was a wish",
                     "`total` asserts the first element exists and is called with an empty array, so it crashes with a TypeError. It should print `3.50` then `0.00`.",
                     'function firstOf(xs: readonly number[]): string {\n'
                     '  return xs[0]!.toFixed(2);\n}\n'
                     'console.log(firstOf([3.5]));\n'
                     'console.log(firstOf([]));\n',
                     'function firstOf(xs: readonly number[]): string {\n'
                     '  return (xs[0] ?? 0).toFixed(2);\n}\n'
                     'console.log(firstOf([3.5]));\n'
                     'console.log(firstOf([]));\n',
                     [("", "3.50\n0.00")],
                     hints=["The ! removed `undefined` from the type and did nothing about the value.",
                            "There is no guard above it, and the second call proves there could not be.",
                            "Supply a default of 0 instead of making a claim."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`must(xs[0], \"first\")` beats `xs[0]!` because…",
                   ["it is shorter", "the failure names what was missing, at the point it was missing",
                    "it is typed", "it is generic"], 1,
                   "Compare a TypeError twenty frames away."),
                _q("A `!` on a value from JSON.parse is…",
                   ["fine", "exactly where you genuinely do not know — so never", "checked",
                    "narrower"], 1,
                   "Lesson 9 is what belongs there."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w15-trycatch", "`try`/`catch` and `unknown`",
            "Anything can be thrown, so a caught value is not an Error.",
            """
Week 8 used `try` at a parsing boundary and week 9 narrowed with
`instanceof Error`. Here is why that narrowing is not optional.

```ts
try {
  risky();
} catch (err) {
  console.log(err.message);
  // ❌ TS18046: 'err' is of type 'unknown'.
}
```

## Why `unknown`

Because JavaScript lets you throw **anything**:

```ts
throw new Error("normal");
throw "a string";
throw { code: 42 };
throw undefined;
```

All legal. So the compiler cannot know that a caught value is an `Error`, and
under `strict` — via `useUnknownInCatchVariables` — it types it `unknown` and
makes you check. (Older code and non-strict projects get `any` here, which is
why so much code reads `err.message` and gets away with it until it does not.)

## The narrowing

```ts
try {
  risky();
} catch (err) {
  const message = err instanceof Error ? err.message : String(err);
  console.log(message);
}
```

That is the whole pattern. Write it once as a helper and stop thinking about it:

```ts
function messageOf(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}
```

`String(e)` is the right fallback: it copes with a thrown string, a number,
`undefined`, and an object (which becomes `"[object Object]"` — ugly, but it
does not throw, which is what matters in an error path).

## The binding is optional

If you do not use the value, leave it out:

```ts
try {
  raw = JSON.parse(text);
} catch {
  return { ok: false, error: "not valid JSON" };
}
```

That is clearer than a bound variable you ignore, and it is exactly what the
capstone does.

## `finally`

Runs whether or not something was thrown, and whether or not you returned:

```ts
try {
  return compute();
} finally {
  cleanup();          // always
}
```

Use it for cleanup — releasing something you acquired. Do not put logic there:
a `return` inside `finally` silently discards whatever the `try` was returning,
which is one of the more baffling bugs available.

## When not to catch

The default should be **not catching**. A `catch` is a claim that you can do
something useful about the failure. If you cannot, letting it propagate is
better: the caller may know more than you.

```ts
try {
  return parse(text);
} catch (err) {
  return null;              // ❌ what went wrong? nobody will ever know
}
```

That is the worst pattern in the lesson. The failure is real, the information is
gone, and the caller gets a `null` that means twelve different things.

Two honest alternatives: **rethrow** with more context, or **return a `Result`**
(lesson 7) that carries the reason.

```ts
try {
  return parse(text);
} catch (err) {
  throw new Error(`parsing line ${n}: ${messageOf(err)}`);
}
```

> ⚠️ **Common mistakes:** `err.message` without narrowing; catching to return
> `null`; a `return` inside `finally`; and catching around a whole function when
> the one line that can fail is in the middle.
""",
            warmup=[
                _q("`catch (err)` types err as…",
                   ["Error", "unknown", "any", "string"], 1,
                   "Anything can be thrown."),
                _q("Reading `err.message` directly gives…",
                   ["the message", "TS18046", "undefined", "any"], 1,
                   "'err' is of type 'unknown'."),
                _q("`catch { … }` with no binding is…",
                   ["a syntax error", "legal when you do not use the value", "non-strict only",
                    "the same as catch (e: any)"], 1,
                   "Clearer than an ignored variable."),
                _q("A `return` inside `finally`…",
                   ["is illegal", "silently discards what the try was returning", "is required",
                    "runs twice"], 1,
                   "Keep logic out of finally."),
            ],
            exercises=[
                _ex("tscourse-w15-tc-1", "Narrow the caught value",
                    "Get a message out of the caught value without assuming it is an Error.",
                    'function risky(n: number): number {\n'
                    '  if (n < 0) {\n    throw new Error("negative");\n  }\n'
                    '  return n;\n}\n'
                    'try {\n  console.log(risky(-1));\n} catch (err) {\n'
                    '  console.log(err instanceof Error ? err.message : String(err));\n}\n',
                    'err instanceof Error ? err.message : String(err)',
                    [("", "negative")],
                    hints=["Test with instanceof, and fall back to String for anything else.",
                           "Write err instanceof Error ? err.message : String(err)"],
                    difficulty="Medium"),
                _ex("tscourse-w15-tc-2", "Write the helper once",
                    "Write `messageOf`, so no other catch block has to think about this again.",
                    'function messageOf(e: unknown): string {\n'
                    '  return e instanceof Error ? e.message : String(e);\n}\n'
                    'try {\n  throw new Error("boom");\n} catch (err) {\n'
                    '  console.log(messageOf(err));\n}\n'
                    'try {\n  throw "just a string";\n} catch (err) {\n'
                    '  console.log(messageOf(err));\n}\n',
                    'return e instanceof Error ? e.message : String(e);',
                    [("", "boom\njust a string")],
                    hints=["The Error branch reads .message; the other converts.",
                           "String(e) never throws, which is what an error path needs."],
                    difficulty="Medium"),
                _ex("tscourse-w15-tc-3", "Drop the binding you do not use",
                    "Catch without naming the value, since the error message here is fixed.",
                    'function parseCount(text: string): number {\n'
                    '  try {\n'
                    '    const n = Number(text);\n'
                    '    if (!Number.isFinite(n)) {\n      throw new Error("nope");\n    }\n'
                    '    return n;\n'
                    '  } catch {\n'
                    '    return 0;\n  }\n}\n'
                    'console.log(`${parseCount("7")} ${parseCount("x")}`);\n',
                    '  } catch {\n', [("", "7 0")],
                    hints=["An optional catch binding: no parentheses at all.",
                           "Write } catch {"],
                    difficulty="Medium"),
                _ex("tscourse-w15-tc-4", "Cleanup that always runs",
                    "Put the closing step where it runs on both paths.",
                    'function withResource(fail: boolean): string {\n'
                    '  const log: string[] = ["open"];\n'
                    '  try {\n'
                    '    if (fail) {\n      throw new Error("boom");\n    }\n'
                    '    log.push("work");\n'
                    '    return log.join(",");\n'
                    '  } catch {\n'
                    '    log.push("caught");\n'
                    '    return log.join(",");\n'
                    '  } finally {\n'
                    '    log.push("close");\n  }\n}\n'
                    'console.log(withResource(false));\n'
                    'console.log(withResource(true));\n',
                    '  } finally {\n'
                    '    log.push("close");\n  }',
                    [("", "open,work\nopen,caught")],
                    hints=["finally runs after the return value has already been computed — which is why \"close\" does not appear in the output.",
                           "That is the point of the exercise: it runs, but it cannot change what was returned.",
                           "Write } finally { and push \"close\"."],
                    difficulty="Medium"),
                _ex("tscourse-w15-tc-5", "Rethrow with context",
                    "Catch, add the line number, and throw on — rather than swallowing it.",
                    'function messageOf(e: unknown): string {\n'
                    '  return e instanceof Error ? e.message : String(e);\n}\n'
                    'function parseAmount(text: string): number {\n'
                    '  const n = Number(text);\n'
                    '  if (!Number.isFinite(n)) {\n    throw new Error(`not a number: ${text}`);\n  }\n'
                    '  return n;\n}\n'
                    'function parseLine(line: string, n: number): number {\n'
                    '  try {\n    return parseAmount(line);\n'
                    '  } catch (err) {\n'
                    '    throw new Error(`line ${n}: ${messageOf(err)}`);\n  }\n}\n'
                    'try {\n  parseLine("lots", 3);\n} catch (err) {\n'
                    '  console.log(messageOf(err));\n}\n',
                    'throw new Error(`line ${n}: ${messageOf(err)}`);',
                    [("", "line 3: not a number: lots")],
                    hints=["Wrap the original message rather than replacing it.",
                           "The new error mentions the line, then the cause."],
                    difficulty="Medium"),
                _diagnose("tscourse-w15-tc-d1", "The caught value that is not an Error",
                          "TS18046: 'err' is of type 'unknown'.",
                          'try {\n  throw new Error("boom");\n} catch (err) {\n'
                          '  console.log(err.message);\n}\n',
                          'try {\n  throw new Error("boom");\n} catch (err) {\n'
                          '  console.log(err instanceof Error ? err.message : String(err));\n}\n',
                          [("", "boom")],
                          hints=["Anything at all can be thrown, so the compiler will not assume this is an Error.",
                                 "Narrow with instanceof, and handle the other case."],
                          difficulty="Medium"),
                _fix("tscourse-w15-tc-fix1", "Fix the catch that swallowed the reason",
                     "`parseAmount` throws a message naming the bad text, and the caller replaces it with a bare `-1` — so the report says nothing useful. It should print `not a number: lots`.",
                     'function parseAmount(text: string): number {\n'
                     '  const n = Number(text);\n'
                     '  if (!Number.isFinite(n)) {\n    throw new Error(`not a number: ${text}`);\n  }\n'
                     '  return n;\n}\n'
                     'function report(text: string): string {\n'
                     '  try {\n    return String(parseAmount(text));\n'
                     '  } catch {\n    return String(-1);\n  }\n}\n'
                     'console.log(report("lots"));\n',
                     'function messageOf(e: unknown): string {\n'
                     '  return e instanceof Error ? e.message : String(e);\n}\n'
                     'function parseAmount(text: string): number {\n'
                     '  const n = Number(text);\n'
                     '  if (!Number.isFinite(n)) {\n    throw new Error(`not a number: ${text}`);\n  }\n'
                     '  return n;\n}\n'
                     'function report(text: string): string {\n'
                     '  try {\n    return String(parseAmount(text));\n'
                     '  } catch (err) {\n    return messageOf(err);\n  }\n}\n'
                     'console.log(report("lots"));\n',
                     [("", "not a number: lots")],
                     hints=["The information was there and the catch threw it away — the worst pattern in the lesson.",
                            "Bind the caught value and narrow it instead of ignoring it.",
                            "Add the messageOf helper and return its result."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`String(e)` as the non-Error fallback is right because…",
                   ["it is short", "it copes with anything and never throws in an error path",
                    "it is typed", "it returns Error"], 1,
                   "An error path must not fail."),
                _q("The default should be…",
                   ["catch everything", "not catching — catch only when you can do something useful",
                    "catch and return null", "catch and log"], 1,
                   "The caller may know more than you."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w15-errors", "Custom error classes",
            "Week 11's classes, doing the job they are best at.",
            """
`new Error("bad row")` tells the caller something went wrong. It does not tell
them **what kind** of thing, and it cannot carry the line number. A subclass does
both.

```ts
class ParseError extends Error {
  readonly line: number;

  constructor(message: string, line: number) {
    super(message);              // FIRST — week 11's rule
    this.name = "ParseError";
    this.line = line;
  }
}
```

Three things to notice:

**`super(message)` comes first.** It is a derived constructor, so week 11's
TS2377 and TS17009 apply unchanged.

**Set `name`.** It is what appears in a stack trace and in `String(err)`.
`Error` sets it to `"Error"`, and the subclass does not update it for you.

**Add whatever fields help.** `line`, a `field` name, an HTTP `status`, the
original cause — this is the entire reason to subclass.

## Narrowing to it

`instanceof` works on your subclass exactly as it does on `Error`:

```ts
try {
  risky();
} catch (err) {
  if (err instanceof ParseError) {
    console.log(`${err.name} at line ${err.line}: ${err.message}`);
  } else if (err instanceof Error) {
    console.log(err.message);
  } else {
    console.log(String(err));
  }
}
```

**Order matters.** `ParseError` *is* an `Error`, so testing `instanceof Error`
first would swallow it and you would never reach the specific branch. Check the
most specific type first — the same rule as any narrowing chain from week 9.

## Several kinds of failure

Once you have two, the `catch` becomes a small dispatch:

```ts
class ParseError extends Error { … }
class ValidationError extends Error {
  readonly field: string;
  constructor(message: string, field: string) {
    super(message);
    this.name = "ValidationError";
    this.field = field;
  }
}
```

and the caller can decide per kind — retry a `ValidationError`, give up on a
`ParseError`. That is the thing a bare `Error` cannot support.

## What this does not solve

A subclass tells you what happened. It does not make the failure part of the
**signature**: `function parse(s: string): Entry` says nothing about throwing,
and nobody is obliged to catch. That is what the next lesson is for.

There is also a standard field for wrapping: `new Error("outer", { cause: err })`
keeps the original. It is well supported and worth knowing, though narrowing
`cause` means narrowing an `unknown` again.

> ⚠️ **Common mistakes:** forgetting `super(message)`; forgetting to set `name`;
> checking `instanceof Error` before the subclass; and inventing five error
> classes where one with a `code` field would have done.
""",
            warmup=[
                _q("In `class ParseError extends Error`, `super(message)` must come…",
                   ["last", "before any use of `this`", "anywhere", "nowhere"], 1,
                   "Week 11's rule, unchanged."),
                _q("`this.name = \"ParseError\"` is needed because…",
                   ["it is required", "Error sets name to \"Error\" and the subclass does not update it",
                    "of instanceof", "of the stack"], 1,
                   "It is what shows up in String(err)."),
                _q("Testing `instanceof Error` before `instanceof ParseError`…",
                   ["is fine", "swallows the subclass — the specific branch is never reached",
                    "is faster", "is required"], 1,
                   "Most specific first."),
                _q("The main reason to subclass Error is…",
                   ["a nicer message", "to carry extra fields and be narrowed to by kind",
                    "performance", "to avoid try"], 1,
                   "That is what a bare Error cannot do."),
            ],
            exercises=[
                _ex("tscourse-w15-er-1", "Call the parent constructor",
                    "Pass the message up to Error before touching `this`.",
                    'class ParseError extends Error {\n'
                    '  readonly line: number;\n\n'
                    '  constructor(message: string, line: number) {\n'
                    '    super(message);\n'
                    '    this.name = "ParseError";\n'
                    '    this.line = line;\n  }\n}\n'
                    'const e = new ParseError("bad row", 3);\n'
                    'console.log(`${e.name}: ${e.message} (line ${e.line})`);\n',
                    'super(message);', [("", "ParseError: bad row (line 3)")],
                    hints=["The parent takes the message.",
                           "Write super(message);"]),
                _ex("tscourse-w15-er-2", "Name it",
                    "Set the name, so it appears in the report rather than the inherited \"Error\".",
                    'class ParseError extends Error {\n'
                    '  readonly line: number;\n\n'
                    '  constructor(message: string, line: number) {\n'
                    '    super(message);\n'
                    '    this.name = "ParseError";\n'
                    '    this.line = line;\n  }\n}\n'
                    'const e = new ParseError("bad row", 3);\n'
                    'console.log(`${e.name}/${new Error("plain").name}`);\n',
                    'this.name = "ParseError";', [("", "ParseError/Error")],
                    hints=["Assign to the inherited name member.",
                           'Write this.name = "ParseError";'],
                    difficulty="Medium"),
                _ex("tscourse-w15-er-3", "Narrow to the subclass",
                    "Test for the specific error first, so its extra field is reachable.",
                    'class ParseError extends Error {\n'
                    '  readonly line: number;\n\n'
                    '  constructor(message: string, line: number) {\n'
                    '    super(message);\n'
                    '    this.name = "ParseError";\n'
                    '    this.line = line;\n  }\n}\n'
                    'function report(err: unknown): string {\n'
                    '  if (err instanceof ParseError) {\n'
                    '    return `${err.name} at line ${err.line}`;\n  }\n'
                    '  if (err instanceof Error) {\n    return err.message;\n  }\n'
                    '  return String(err);\n}\n'
                    'console.log(report(new ParseError("bad", 3)));\n'
                    'console.log(report(new Error("plain")));\n'
                    'console.log(report("raw"));\n',
                    'if (err instanceof ParseError) {\n'
                    '    return `${err.name} at line ${err.line}`;\n  }',
                    [("", "ParseError at line 3\nplain\nraw")],
                    hints=["The most specific test has to come first, or the Error branch takes it.",
                           "Inside that branch, `line` is available."],
                    difficulty="Medium"),
                _ex("tscourse-w15-er-4", "Two kinds of failure",
                    "Add the validation error's field, so the caller can report which field was wrong.",
                    'class ParseError extends Error {\n'
                    '  constructor(message: string) {\n'
                    '    super(message);\n    this.name = "ParseError";\n  }\n}\n'
                    'class ValidationError extends Error {\n'
                    '  readonly field: string;\n\n'
                    '  constructor(message: string, field: string) {\n'
                    '    super(message);\n'
                    '    this.name = "ValidationError";\n'
                    '    this.field = field;\n  }\n}\n'
                    'function report(err: unknown): string {\n'
                    '  if (err instanceof ValidationError) {\n'
                    '    return `${err.field}: ${err.message}`;\n  }\n'
                    '  if (err instanceof ParseError) {\n    return `parse: ${err.message}`;\n  }\n'
                    '  return "unknown";\n}\n'
                    'console.log(report(new ValidationError("must be a number", "cents")));\n'
                    'console.log(report(new ParseError("bad row")));\n',
                    'readonly field: string;', [("", "cents: must be a number\nparse: bad row")],
                    hints=["One readonly field, assigned in the constructor.",
                           "Write readonly field: string;"],
                    difficulty="Medium"),
                _diagnose("tscourse-w15-er-d1", "The field the base class lacks",
                          "TS2339: Property 'line' does not exist on type 'Error'.",
                          'class ParseError extends Error {\n'
                          '  readonly line: number;\n\n'
                          '  constructor(message: string, line: number) {\n'
                          '    super(message);\n'
                          '    this.name = "ParseError";\n'
                          '    this.line = line;\n  }\n}\n'
                          'function report(err: unknown): string {\n'
                          '  if (err instanceof Error) {\n'
                          '    return `line ${err.line}`;\n  }\n'
                          '  return "unknown";\n}\n'
                          'console.log(report(new ParseError("bad", 3)));\n',
                          'class ParseError extends Error {\n'
                          '  readonly line: number;\n\n'
                          '  constructor(message: string, line: number) {\n'
                          '    super(message);\n'
                          '    this.name = "ParseError";\n'
                          '    this.line = line;\n  }\n}\n'
                          'function report(err: unknown): string {\n'
                          '  if (err instanceof ParseError) {\n'
                          '    return `line ${err.line}`;\n  }\n'
                          '  return "unknown";\n}\n'
                          'console.log(report(new ParseError("bad", 3)));\n',
                          [("", "line 3")],
                          hints=["The guard narrowed to Error, and `line` belongs to the subclass.",
                                 "Narrow to the specific class instead."],
                          difficulty="Medium"),
                _fix("tscourse-w15-er-fix1", "Fix the narrowing order",
                     "`instanceof Error` is tested first, and a ParseError is an Error — so the specific branch is never reached and this prints `bad` instead of `ParseError at line 3`.",
                     'class ParseError extends Error {\n'
                     '  readonly line: number;\n\n'
                     '  constructor(message: string, line: number) {\n'
                     '    super(message);\n'
                     '    this.name = "ParseError";\n'
                     '    this.line = line;\n  }\n}\n'
                     'function report(err: unknown): string {\n'
                     '  if (err instanceof Error) {\n    return err.message;\n  }\n'
                     '  if (err instanceof ParseError) {\n'
                     '    return `${err.name} at line ${err.line}`;\n  }\n'
                     '  return String(err);\n}\n'
                     'console.log(report(new ParseError("bad", 3)));\n',
                     'class ParseError extends Error {\n'
                     '  readonly line: number;\n\n'
                     '  constructor(message: string, line: number) {\n'
                     '    super(message);\n'
                     '    this.name = "ParseError";\n'
                     '    this.line = line;\n  }\n}\n'
                     'function report(err: unknown): string {\n'
                     '  if (err instanceof ParseError) {\n'
                     '    return `${err.name} at line ${err.line}`;\n  }\n'
                     '  if (err instanceof Error) {\n    return err.message;\n  }\n'
                     '  return String(err);\n}\n'
                     'console.log(report(new ParseError("bad", 3)));\n',
                     [("", "ParseError at line 3")],
                     hints=["Both branches are reachable and well typed, so nothing was reported.",
                            "A subclass instance satisfies `instanceof` on the parent as well.",
                            "Put the most specific test first."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Five error classes where one with a `code` field would do is…",
                   ["good design", "over-modelling", "required", "faster"], 1,
                   "Subclass when callers genuinely branch on the kind."),
                _q("A subclass still does not…",
                   ["carry fields", "make the failure part of the function's signature",
                    "work with instanceof", "set a name"], 1,
                   "Which is what Result does."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w15-result", "The `Result` pattern",
            "Returning failure instead of throwing it.",
            """
Look at this signature and say what can go wrong:

```ts
function parseAmount(text: string): number
```

Nothing in it mentions failure. It might throw; you would only know by reading
the body, and nothing obliges the caller to handle it. Compare:

```ts
type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: string };

function parseAmount(text: string): Result<number>
```

Now failure is **in the type**. The caller cannot reach `.value` without dealing
with the other case, because the compiler will not let them.

You have both halves of this already: week 9's discriminated unions and week 10's
generic `Result<T>`. This is the pattern they were for.

## Using it

```ts
function parseAmount(text: string): Result<number> {
  const n = Number(text);
  if (!Number.isFinite(n)) {
    return { ok: false, error: `not a number: ${text}` };
  }
  return { ok: true, value: n };
}

const r = parseAmount("3.5");
console.log(r.ok ? r.value.toFixed(2) : r.error);
```

Reaching straight for `.value` is an error, which is the whole point:

```ts
console.log(r.value);
// ❌ TS2339: Property 'value' does not exist on type 'Result<number>'.
//            Property 'value' does not exist on type '{ ok: false; error: string; }'.
```

`ok` is the discriminant. Test it and the union collapses to one member — exactly
week 9's narrowing.

## Collecting results

The common shape: many things to parse, first failure wins.

```ts
function parseAll(texts: readonly string[]): Result<readonly number[]> {
  const out: number[] = [];
  for (const t of texts) {
    const r = parseAmount(t);
    if (!r.ok) {
      return r;                  // the failure type already matches
    }
    out.push(r.value);
  }
  return { ok: true, value: out };
}
```

Note `return r` on the failure path: a `Result<number>` failure member and a
`Result<readonly number[]>` failure member are the same shape, so it just
type-checks. And note the local `out` array — week 13's rules are about values
that escape; a local accumulator that never leaves the function is fine.

## Throw or return?

The useful line:

**Return a `Result` for an expected failure.** Something that is part of the
contract and that a caller will routinely hit: bad user input, a record that is
not there, a validation failure. These are not exceptional; they are half of what
the function does.

**Throw for an unexpected failure.** A bug, a broken invariant, a condition
nobody up the stack can do anything about: out of memory, a config file missing
at startup, an array index that should have been in range. Wrapping those in a
`Result` just means every caller writes `if (!r.ok) throw ...`.

The smell in each direction: if callers routinely `try/catch` around a call, it
should probably return a `Result`. If callers routinely ignore an `ok: false`, it
should probably have thrown.

## The cost, honestly

`Result` is more verbose. Every call site gets an `if`, and there is no automatic
propagation — languages with `?` or `do` notation make this cheap, and TypeScript
does not. A deep chain of Results is genuinely more annoying than a chain of
throws.

Which is why the answer is not "always Result". It is: **use it at boundaries**,
where failure is expected and the caller must decide — parsing, validating,
looking things up. Inside a trusted core, throw.

A richer error type is a small step up when a string is not enough:

```ts
type Result<T, E = string> =
  | { ok: true; value: T }
  | { ok: false; error: E };
```

With `E` defaulting to `string` (week 10's default type parameter), the simple
case stays simple.

> ⚠️ **Common mistakes:** reaching for `.value` without checking `ok`; using
> `Result` for programmer errors, so every caller rethrows; and an `error: string`
> that loses which field was wrong — the capstone's messages name the field on
> purpose.
""",
            warmup=[
                _q("`function parseAmount(text: string): number` tells the caller about failure…",
                   ["fully", "not at all", "via a comment", "via unknown"], 1,
                   "Throwing is invisible in a signature."),
                _q("`r.value` without checking `r.ok` gives…",
                   ["the value", "TS2339", "undefined", "any"], 1,
                   "The discriminant has to be tested first."),
                _q("Return a Result for…",
                   ["bugs", "expected failures that are part of the contract", "everything",
                    "nothing"], 1,
                   "Bad input, not found, validation."),
                _q("Throw for…",
                   ["bad user input", "unexpected failures nobody up the stack can handle",
                    "validation", "lookups"], 1,
                   "Otherwise every caller just rethrows."),
            ],
            exercises=[
                _ex("tscourse-w15-rs-1", "Declare the union",
                    "Write the Result type: either a value, or an error message.",
                    'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };\n'
                    'const good: Result<number> = { ok: true, value: 3 };\n'
                    'const bad: Result<number> = { ok: false, error: "nope" };\n'
                    'console.log(`${good.ok} ${bad.ok}`);\n',
                    'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };',
                    [("", "true false")],
                    hints=["Two members, discriminated by a literal boolean.",
                           "The success member carries `value: T`; the failure member carries `error: string`."],
                    difficulty="Medium"),
                _ex("tscourse-w15-rs-2", "Return failure instead of throwing",
                    "Report the bad input as a value rather than an exception.",
                    'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };\n'
                    'function parseAmount(text: string): Result<number> {\n'
                    '  const n = Number(text);\n'
                    '  if (!Number.isFinite(n)) {\n'
                    '    return { ok: false, error: `not a number: ${text}` };\n  }\n'
                    '  return { ok: true, value: n };\n}\n'
                    'const a = parseAmount("3.5");\n'
                    'const b = parseAmount("lots");\n'
                    'console.log(a.ok ? a.value.toFixed(2) : a.error);\n'
                    'console.log(b.ok ? b.value.toFixed(2) : b.error);\n',
                    'return { ok: false, error: `not a number: ${text}` };',
                    [("", "3.50\nnot a number: lots")],
                    hints=["No throw — build the failure member and return it.",
                           "The message names the offending text."],
                    difficulty="Medium"),
                _ex("tscourse-w15-rs-3", "Narrow on the discriminant",
                    "Check `ok` so both members can be handled.",
                    'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };\n'
                    'function describe(r: Result<number>): string {\n'
                    '  if (r.ok) {\n    return `got ${r.value}`;\n  }\n'
                    '  return `failed: ${r.error}`;\n}\n'
                    'console.log(describe({ ok: true, value: 7 }));\n'
                    'console.log(describe({ ok: false, error: "nope" }));\n',
                    'if (r.ok) {\n    return `got ${r.value}`;\n  }',
                    [("", "got 7\nfailed: nope")],
                    hints=["Test the discriminant, and the union collapses to one member inside.",
                           "`r.value` is only available in that branch."],
                    difficulty="Medium"),
                _ex("tscourse-w15-rs-4", "First failure wins",
                    "Return the failure straight through when any element fails to parse.",
                    'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };\n'
                    'function parseAmount(text: string): Result<number> {\n'
                    '  const n = Number(text);\n'
                    '  return Number.isFinite(n)\n'
                    '    ? { ok: true, value: n }\n'
                    '    : { ok: false, error: `not a number: ${text}` };\n}\n'
                    'function parseAll(texts: readonly string[]): Result<readonly number[]> {\n'
                    '  const out: number[] = [];\n'
                    '  for (const t of texts) {\n'
                    '    const r = parseAmount(t);\n'
                    '    if (!r.ok) {\n      return r;\n    }\n'
                    '    out.push(r.value);\n  }\n'
                    '  return { ok: true, value: out };\n}\n'
                    'const a = parseAll(["1", "2"]);\n'
                    'const b = parseAll(["1", "x", "3"]);\n'
                    'console.log(a.ok ? a.value.join("+") : a.error);\n'
                    'console.log(b.ok ? b.value.join("+") : b.error);\n',
                    'if (!r.ok) {\n      return r;\n    }',
                    [("", "1+2\nnot a number: x")],
                    hints=["The failure member of Result<number> is the same shape as the failure member of Result<readonly number[]>.",
                           "So the failure can be returned unchanged.",
                           "Write if (!r.ok) { return r; }"],
                    difficulty="Medium"),
                _ex("tscourse-w15-rs-5", "A richer error type",
                    "Give the error parameter a default, so the simple case stays simple.",
                    'type Result<T, E = string> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: E };\n'
                    'interface FieldError {\n  readonly field: string;\n  readonly reason: string;\n}\n'
                    'const plain: Result<number> = { ok: false, error: "nope" };\n'
                    'const rich: Result<number, FieldError> = {\n'
                    '  ok: false,\n  error: { field: "cents", reason: "must be a number" },\n};\n'
                    'console.log(plain.ok ? "?" : plain.error);\n'
                    'console.log(rich.ok ? "?" : `${rich.error.field}: ${rich.error.reason}`);\n',
                    'type Result<T, E = string> =',
                    [("", "nope\ncents: must be a number")],
                    hints=["A second type parameter with a default, from week 10.",
                           "Write type Result<T, E = string> ="],
                    difficulty="Medium"),
                _diagnose("tscourse-w15-rs-d1", "The member that might not be there",
                          "TS2339: Property 'value' does not exist on type 'Result<number>'.",
                          'type Result<T> =\n'
                          '  | { ok: true; value: T }\n'
                          '  | { ok: false; error: string };\n'
                          'function parseAmount(text: string): Result<number> {\n'
                          '  const n = Number(text);\n'
                          '  return Number.isFinite(n)\n'
                          '    ? { ok: true, value: n }\n'
                          '    : { ok: false, error: `not a number: ${text}` };\n}\n'
                          'const r = parseAmount("3.5");\n'
                          'console.log(r.value.toFixed(2));\n',
                          'type Result<T> =\n'
                          '  | { ok: true; value: T }\n'
                          '  | { ok: false; error: string };\n'
                          'function parseAmount(text: string): Result<number> {\n'
                          '  const n = Number(text);\n'
                          '  return Number.isFinite(n)\n'
                          '    ? { ok: true, value: n }\n'
                          '    : { ok: false, error: `not a number: ${text}` };\n}\n'
                          'const r = parseAmount("3.5");\n'
                          'console.log(r.ok ? r.value.toFixed(2) : r.error);\n',
                          [("", "3.50")],
                          hints=["This refusal is the entire benefit of the pattern.",
                                 "Test the discriminant, and handle the failure member too."],
                          difficulty="Medium"),
                _fix("tscourse-w15-rs-fix1", "Fix the Result that lost the reason",
                     "`parseAll` discards each element's message and substitutes a generic one, so the report cannot say which value was bad — this prints `bad input` instead of `not a number: x`.",
                     'type Result<T> =\n'
                     '  | { ok: true; value: T }\n'
                     '  | { ok: false; error: string };\n'
                     'function parseAmount(text: string): Result<number> {\n'
                     '  const n = Number(text);\n'
                     '  return Number.isFinite(n)\n'
                     '    ? { ok: true, value: n }\n'
                     '    : { ok: false, error: `not a number: ${text}` };\n}\n'
                     'function parseAll(texts: readonly string[]): Result<readonly number[]> {\n'
                     '  const out: number[] = [];\n'
                     '  for (const t of texts) {\n'
                     '    const r = parseAmount(t);\n'
                     '    if (!r.ok) {\n      return { ok: false, error: "bad input" };\n    }\n'
                     '    out.push(r.value);\n  }\n'
                     '  return { ok: true, value: out };\n}\n'
                     'const b = parseAll(["1", "x", "3"]);\n'
                     'console.log(b.ok ? b.value.join("+") : b.error);\n',
                     'type Result<T> =\n'
                     '  | { ok: true; value: T }\n'
                     '  | { ok: false; error: string };\n'
                     'function parseAmount(text: string): Result<number> {\n'
                     '  const n = Number(text);\n'
                     '  return Number.isFinite(n)\n'
                     '    ? { ok: true, value: n }\n'
                     '    : { ok: false, error: `not a number: ${text}` };\n}\n'
                     'function parseAll(texts: readonly string[]): Result<readonly number[]> {\n'
                     '  const out: number[] = [];\n'
                     '  for (const t of texts) {\n'
                     '    const r = parseAmount(t);\n'
                     '    if (!r.ok) {\n      return r;\n    }\n'
                     '    out.push(r.value);\n  }\n'
                     '  return { ok: true, value: out };\n}\n'
                     'const b = parseAll(["1", "x", "3"]);\n'
                     'console.log(b.ok ? b.value.join("+") : b.error);\n',
                     [("", "not a number: x")],
                     hints=["The specific message existed and was thrown away — the same mistake as swallowing an exception.",
                            "The failure member already has the right shape for this function's Result.",
                            "Return `r` unchanged."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("If callers routinely try/catch around your function, it should probably…",
                   ["throw more", "return a Result", "return null", "log"], 1,
                   "The failure is expected, so put it in the type."),
                _q("The honest cost of Result is…",
                   ["performance", "verbosity — no automatic propagation in TypeScript",
                    "type safety", "nothing"], 1,
                   "Which is why it belongs at boundaries, not everywhere."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w15-json", "`JSON.parse` returns `any`",
            "The one line where the type system switches off.",
            """
Serialising is the easy half:

```ts
const entry = { desc: "coffee", cents: 325 };
const text = JSON.stringify(entry);      // '{"desc":"coffee","cents":325}'
```

Reading it back is where fourteen weeks of guarantees end.

```ts
const data = JSON.parse(text);
```

`data` is **`any`**. Not `object`, not `unknown` — `any`, the type that means
"stop checking". And `any` is contagious: every expression derived from it is
also `any`.

```ts
console.log(data.desc);                    // fine, and correct
console.log(data.nope.deeper.still);       // compiles. Crashes at runtime.
console.log(data.cents.toFixed(2));        // compiles even if cents is "lots"
const n: number = data.cents;              // compiles. n might be a string.
```

Nothing above is reported. That last line is the worst: a `string` is now sitting
in a binding the compiler believes is a `number`, and every downstream function
that takes a `number` will accept it.

## Why the declaration is right

TypeScript genuinely cannot know what is in that text. The alternative would be
`unknown`, and that is what most people wish it returned — but it was declared
`any` long before `unknown` existed, and changing it now would break an enormous
amount of code. So the language leaves it and expects you to do the right thing
at the call site.

## What people do instead, and why it is worse

```ts
const data = JSON.parse(text) as Entry;
```

This *looks* careful. It is a lie with a straight face: `as` performs no check
(week 12), so this claims a shape nobody verified. The `any` was at least
honest about knowing nothing; the assertion replaces honest ignorance with false
confidence, and it is how `{"cents": "lots"}` ends up inside a typed program.

## The honest first move

Annotate it `unknown`:

```ts
const raw: unknown = JSON.parse(text);

console.log(raw.desc);
// ❌ TS18046: 'raw' is of type 'unknown'.
```

That error is the point. `unknown` accepts anything and permits nothing, so the
compiler now *forces* you to check before reading — which is exactly the position
you are actually in. Lesson 9 is how you do the checking.

## What JSON loses in the round trip

Worth knowing, because it surprises people:

```ts
JSON.stringify({ when: new Date(), n: undefined, f: () => 1 });
// {"when":"2026-09-09T00:00:00.000Z"}
```

* A `Date` becomes a **string**. Parsing it back gives you a string, not a Date —
  and if your type says `Date`, your type is now wrong.
* `undefined` members, functions and symbols are **dropped** entirely.
* `Map`, `Set` and class instances lose everything but their plain own
  properties — a parsed `Entry` is not an `Entry` instance, it is a plain object
  that happens to have the same members.
* `NaN` and `Infinity` become `null`.

So even a *correct* round trip does not give you back what you put in. Any type
you claim for parsed JSON has to describe the JSON, not the original value.

> ⚠️ **Common mistakes:** `as SomeType` on parsed JSON; letting the `any` spread
> into a variable and forgetting where it came from; and expecting a parsed
> object to be an instance of the class it was serialised from.
""",
            warmup=[
                _q("`JSON.parse(text)` returns…",
                   ["unknown", "any", "object", "string"], 1,
                   "The type that means stop checking."),
                _q("`data.nope.deeper` on that value…",
                   ["is a type error", "compiles, and crashes at runtime", "is undefined",
                    "is unknown"], 1,
                   "`any` is contagious."),
                _q("`JSON.parse(text) as Entry` is…",
                   ["a check", "an unchecked claim — worse than the any", "safe", "narrowing"], 1,
                   "It replaces honest ignorance with false confidence."),
                _q("`const raw: unknown = JSON.parse(text)` is better because…",
                   ["it is shorter", "unknown permits nothing until you check",
                    "it is faster", "it validates"], 1,
                   "The compiler now forces the check."),
            ],
            exercises=[
                _ex("tscourse-w15-js-1", "Serialise",
                    "Turn the entry into JSON text.",
                    'const entry = { desc: "coffee", cents: 325 };\n'
                    'console.log(JSON.stringify(entry));\n',
                    'JSON.stringify(entry)', [("", '{"desc":"coffee","cents":325}')],
                    hints=["One call, no extra arguments.",
                           "Write JSON.stringify(entry)"]),
                _ex("tscourse-w15-js-2", "Admit you know nothing",
                    "Annotate the parsed value so the compiler will not let you read it unchecked.",
                    _LINE +
                    'const raw: unknown = JSON.parse(line);\n'
                    'console.log(typeof raw === "object" && raw !== null ? "an object" : "something else");\n',
                    'const raw: unknown = JSON.parse(line);',
                    [('{"desc":"coffee"}', "an object"),
                     ('42', "something else")],
                    hints=["The annotation is what turns the `any` into something safe.",
                           "Write const raw: unknown = JSON.parse(line);"],
                    difficulty="Medium"),
                _ex("tscourse-w15-js-3", "What the round trip loses",
                    "Serialise the object and report which keys survived.",
                    'const value = { desc: "coffee", cents: 325, tag: undefined };\n'
                    'const text = JSON.stringify(value);\n'
                    'const back: unknown = JSON.parse(text);\n'
                    'console.log(typeof back === "object" && back !== null ? Object.keys(back).join(",") : "?");\n',
                    'const text = JSON.stringify(value);',
                    [("", "desc,cents")],
                    hints=["An undefined member is dropped rather than serialised as null.",
                           "Write const text = JSON.stringify(value);"],
                    difficulty="Medium"),
                _ex("tscourse-w15-js-4", "A Date does not come back",
                    "Report the runtime type of the `when` member after the round trip.",
                    'const text = JSON.stringify({ when: new Date(0) });\n'
                    'const back: unknown = JSON.parse(text);\n'
                    'const o = typeof back === "object" && back !== null ? (back as Record<string, unknown>) : {};\n'
                    'console.log(typeof o.when);\n',
                    'console.log(typeof o.when);', [("", "string")],
                    hints=["JSON has no date type, so a Date is serialised as text.",
                           "Ask the value what it is at runtime."],
                    difficulty="Medium"),
                _retype("tscourse-w15-js-rt1", "Replace the `any`s",
                        "This program compiles and runs, and every type in it is `any` — so none "
                        "of them mean anything. Give the payload a real type and drop the `any` "
                        "annotations. (The `as` is still an unchecked claim; lesson 9 earns it "
                        "properly.)",
                        _LINE +
                        'const data: any = JSON.parse(line);\n'
                        'const items: any = data.items;\n'
                        'const total: any = items.reduce((s: any, n: any) => s + n, 0);\n'
                        'console.log(total);\n',
                        _LINE +
                        'interface Payload {\n  readonly items: readonly number[];\n}\n'
                        'const data = JSON.parse(line) as Payload;\n'
                        'const items: readonly number[] = data.items;\n'
                        'const total: number = items.reduce((s, n) => s + n, 0);\n'
                        'console.log(total);\n',
                        """
type _1 = Expect<Equal<typeof total, number>>;
type _2 = Expect<Equal<typeof items, readonly number[]>>;
""",
                        [('{"items":[1,2,3]}', "6"),
                         ('{"items":[10]}', "10")],
                        hints=["Declare an interface for the payload: one member, `items`, a readonly array of numbers.",
                               "Then the reduce needs no parameter annotations at all — they are inferred.",
                               "`total` is a number, and `items` is a readonly number[]. The assertions check exactly that."],
                        difficulty="Medium"),
                _diagnose("tscourse-w15-js-d1", "unknown permits nothing",
                          "TS18046: 'raw' is of type 'unknown'.",
                          _LINE +
                          'const raw: unknown = JSON.parse(line);\n'
                          'console.log(raw.desc);\n',
                          _LINE +
                          'const raw: unknown = JSON.parse(line);\n'
                          'const o = typeof raw === "object" && raw !== null ? (raw as Record<string, unknown>) : {};\n'
                          'console.log(typeof o.desc === "string" ? o.desc : "missing");\n',
                          [('{"desc":"coffee"}', "coffee"),
                           ('42', "missing")],
                          hints=["This error is what you asked for by annotating it `unknown` — do not undo the annotation.",
                                 "Check that it is a non-null object first, then treat it as a bag of unknown members.",
                                 "Then check that `desc` really is a string before printing it."],
                          difficulty="Medium"),
                _fix("tscourse-w15-js-fix1", "Fix the assertion that let bad data in",
                     "`as Entry` claims a shape nobody checked, so a `cents` of `\"lots\"` sails through and `.toFixed` crashes at runtime. It should print `3.25` for good input and `bad cents` for the string.",
                     _LINE +
                     'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                     'const entry = JSON.parse(line) as Entry;\n'
                     'console.log((entry.cents / 100).toFixed(2));\n',
                     _LINE +
                     'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                     'const raw: unknown = JSON.parse(line);\n'
                     'const o = typeof raw === "object" && raw !== null ? (raw as Record<string, unknown>) : {};\n'
                     'if (typeof o.desc !== "string" || typeof o.cents !== "number") {\n'
                     '  console.log("bad cents");\n'
                     '} else {\n'
                     '  const entry: Entry = { desc: o.desc, cents: o.cents };\n'
                     '  console.log((entry.cents / 100).toFixed(2));\n}\n',
                     [('{"desc":"coffee","cents":325}', "3.25"),
                      ('{"desc":"coffee","cents":"lots"}', "bad cents")],
                     hints=["The assertion checked nothing, so the string was typed `number` and `.toFixed` was called on it.",
                            "Annotate the parsed value `unknown`, then narrow: a non-null object, then a bag of unknown members.",
                            "Check both members with typeof before building the Entry, and print `bad cents` when either fails."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A parsed object is an instance of the class it came from…",
                   ["yes", "no — it is a plain object with the same members", "with a cast",
                    "under strict"], 1,
                   "instanceof will be false."),
                _q("A `Date` survives a JSON round trip as…",
                   ["a Date", "a string", "a number", "null"], 1,
                   "So a type claiming Date would be wrong."),
            ],
        ),
        # ---- Lesson 9 --------------------------------------------------
        _lesson(
            "w15-validate", "Earning a type from untrusted data",
            "Check once, at the boundary, and never again.",
            """
Lesson 8 left you with an `unknown` and a compiler that will not let you read it.
Good. Now earn the type.

## A type guard that actually checks

Week 9 introduced `v is T` predicates. This is what they are for:

```ts
interface Entry {
  readonly desc: string;
  readonly cents: number;
}

function isEntry(v: unknown): v is Entry {
  if (typeof v !== "object" || v === null) {
    return false;
  }
  const o = v as Record<string, unknown>;
  return typeof o.desc === "string" && typeof o.cents === "number";
}
```

Read it in three steps:

1. **Is it an object at all?** With the `!== null` from lesson 1, because
   `typeof null` is `"object"`.
2. **`v as Record<string, unknown>`** — the one assertion in the whole pattern,
   and it is **earned**: the guard above proves `v` is a non-null object, and
   every property of any object is legitimately `unknown`. Note what it does not
   claim: not that `desc` exists, not that anything has a type.
3. **Check each member** with `typeof`. Now `o.desc` narrows to `string` and
   `o.cents` to `number`.

Used at the boundary:

```ts
const raw: unknown = JSON.parse(text);
if (!isEntry(raw)) {
  return { ok: false, error: "not an entry" };
}
raw.cents.toFixed(2);        // a fact, not a hope
```

## The compiler trusts you here

`v is Entry` is a **promise**, not a proof. Write a guard that forgets to check
`cents` and the compiler believes you anyway — the same hole week 14's
`isDiscretionary` fix showed. A guard body is one of the few places in TypeScript
where you must be careful by hand, so keep guards small, obvious, and one per
type.

## Say which field was wrong

A boolean guard tells the caller "no". For anything a human will read, that is
not enough. Combine it with lesson 7:

```ts
type Result<T> = { ok: true; value: T } | { ok: false; error: string };

function parseEntry(v: unknown, where: string): Result<Entry> {
  if (typeof v !== "object" || v === null) {
    return { ok: false, error: `${where} must be an object` };
  }
  const o = v as Record<string, unknown>;
  if (typeof o.desc !== "string") {
    return { ok: false, error: `${where}.desc must be a string` };
  }
  if (typeof o.cents !== "number") {
    return { ok: false, error: `${where}.cents must be a number` };
  }
  return { ok: true, value: { desc: o.desc, cents: o.cents } };
}
```

Longer, and worth it: `entries[2].cents must be a number` is an error somebody
can act on. This is the capstone.

Note the `where` parameter threading a path through — that is how validators
report position, and it costs one argument.

## Arrays

`Array.isArray` narrows an `unknown`, though it lands on `any[]`, so pin it
immediately:

```ts
if (!Array.isArray(v)) {
  return { ok: false, error: "expected an array" };
}
const list: readonly unknown[] = v;      // pin it before reading anything
```

Then validate element by element, carrying the index into the message.

## Parse, don't validate

The principle behind all of this. A `validate(v): boolean` leaves you holding the
same untrusted value and hoping everyone remembers to have called it. A
`parse(v): Result<Entry>` hands back a **different, trusted type** — and then the
absence of checks everywhere else is not laziness, it is a guarantee.

Do it once, at the edge. Everything inside is typed and stays typed.

## In real projects

You would reach for a schema library — Zod, Valibot, io-ts — which generate both
the runtime check and the TypeScript type from one declaration, so they cannot
drift. Worth knowing they exist, and worth having written this by hand once, so
you know exactly what they are doing for you.

> ⚠️ **Common mistakes:** a guard that checks some members and claims all of
> them; validating deep inside the program instead of at the boundary; and
> `Array.isArray` followed by reading elements as `any`.
""",
            warmup=[
                _q("`typeof v !== \"object\" || v === null` is needed because…",
                   ["objects are rare", "typeof null is \"object\"", "of arrays",
                    "of unknown"], 1,
                   "Lesson 1's wart."),
                _q("`v as Record<string, unknown>` inside a guard is earned because…",
                   ["assertions are fine", "the check above proves v is a non-null object",
                    "unknown allows it", "guards are exempt"], 1,
                   "And it claims nothing about the members."),
                _q("A `v is T` predicate is…",
                   ["proved by the compiler", "a promise the compiler takes on trust",
                    "a runtime type", "the same as a cast"], 1,
                   "So the body has to be right by hand."),
                _q("\"Parse, don't validate\" means the function returns…",
                   ["a boolean", "a different, trusted TYPE", "void", "unknown"], 1,
                   "Then no later check is needed."),
            ],
            exercises=[
                _ex("tscourse-w15-va-1", "The object check",
                    "Reject anything that is not a non-null object, before treating it as one.",
                    _LINE +
                    'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                    'function isEntry(v: unknown): v is Entry {\n'
                    '  if (typeof v !== "object" || v === null) {\n    return false;\n  }\n'
                    '  const o = v as Record<string, unknown>;\n'
                    '  return typeof o.desc === "string" && typeof o.cents === "number";\n}\n'
                    'const raw: unknown = JSON.parse(line);\n'
                    'console.log(isEntry(raw) ? `${raw.desc} ${raw.cents}` : "invalid");\n',
                    'if (typeof v !== "object" || v === null) {\n    return false;\n  }',
                    [('{"desc":"coffee","cents":325}', "coffee 325"),
                     ('null', "invalid"),
                     ('42', "invalid")],
                    hints=["Two conditions, because typeof null is \"object\".",
                           "Return false when either fails."],
                    difficulty="Medium"),
                _ex("tscourse-w15-va-2", "Check every member",
                    "Complete the guard by checking both members' runtime types.",
                    _LINE +
                    'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                    'function isEntry(v: unknown): v is Entry {\n'
                    '  if (typeof v !== "object" || v === null) {\n    return false;\n  }\n'
                    '  const o = v as Record<string, unknown>;\n'
                    '  return typeof o.desc === "string" && typeof o.cents === "number";\n}\n'
                    'const raw: unknown = JSON.parse(line);\n'
                    'console.log(isEntry(raw) ? `${raw.desc} ${raw.cents}` : "invalid");\n',
                    'return typeof o.desc === "string" && typeof o.cents === "number";',
                    [('{"desc":"coffee","cents":325}', "coffee 325"),
                     ('{"desc":"coffee","cents":"lots"}', "invalid"),
                     ('{"cents":325}', "invalid")],
                    hints=["Both members, joined with &&.",
                           "The compiler trusts this line, so it has to cover every member of Entry."],
                    difficulty="Medium"),
                _ex("tscourse-w15-va-3", "Name the field that failed",
                    "Return the failure that says which member was wrong, rather than a bare false.",
                    _LINE +
                    'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };\n'
                    'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                    'function parseEntry(v: unknown, where: string): Result<Entry> {\n'
                    '  if (typeof v !== "object" || v === null) {\n'
                    '    return { ok: false, error: `${where} must be an object` };\n  }\n'
                    '  const o = v as Record<string, unknown>;\n'
                    '  if (typeof o.desc !== "string") {\n'
                    '    return { ok: false, error: `${where}.desc must be a string` };\n  }\n'
                    '  if (typeof o.cents !== "number") {\n'
                    '    return { ok: false, error: `${where}.cents must be a number` };\n  }\n'
                    '  return { ok: true, value: { desc: o.desc, cents: o.cents } };\n}\n'
                    'const raw: unknown = JSON.parse(line);\n'
                    'const r = parseEntry(raw, "entry");\n'
                    'console.log(r.ok ? `${r.value.desc} ${r.value.cents}` : r.error);\n',
                    'if (typeof o.cents !== "number") {\n'
                    '    return { ok: false, error: `${where}.cents must be a number` };\n  }',
                    [('{"desc":"coffee","cents":325}', "coffee 325"),
                     ('{"desc":"coffee","cents":"lots"}', "entry.cents must be a number"),
                     ('{"desc":"coffee"}', "entry.cents must be a number")],
                    hints=["Mirror the `desc` check above it, for the other member.",
                           "The message names the path and what was expected."],
                    difficulty="Medium"),
                _ex("tscourse-w15-va-4", "Pin the array",
                    "Narrow to an array and immediately give it an honest element type.",
                    _LINE +
                    'const raw: unknown = JSON.parse(line);\n'
                    'if (!Array.isArray(raw)) {\n'
                    '  console.log("expected an array");\n'
                    '} else {\n'
                    '  const list: readonly unknown[] = raw;\n'
                    '  console.log(`${list.length} items`);\n}\n',
                    'const list: readonly unknown[] = raw;',
                    [('[1,2,3]', "3 items"),
                     ('{"a":1}', "expected an array")],
                    hints=["Array.isArray narrows to any[], which is not what you want to read from.",
                           "Assign it to a readonly array of unknown before touching it."],
                    difficulty="Medium"),
                _ex("tscourse-w15-va-5", "Validate every element, with its index",
                    "Carry the index into the path, so the message points at the offending element.",
                    _LINE +
                    'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };\n'
                    'function parseAmount(v: unknown, where: string): Result<number> {\n'
                    '  return typeof v === "number"\n'
                    '    ? { ok: true, value: v }\n'
                    '    : { ok: false, error: `${where} must be a number` };\n}\n'
                    'function parseAll(list: readonly unknown[]): Result<readonly number[]> {\n'
                    '  const out: number[] = [];\n'
                    '  for (let i = 0; i < list.length; i = i + 1) {\n'
                    '    const r = parseAmount(list[i], `items[${i}]`);\n'
                    '    if (!r.ok) {\n      return r;\n    }\n'
                    '    out.push(r.value);\n  }\n'
                    '  return { ok: true, value: out };\n}\n'
                    'const raw: unknown = JSON.parse(line);\n'
                    'const list: readonly unknown[] = Array.isArray(raw) ? raw : [];\n'
                    'const r = parseAll(list);\n'
                    'console.log(r.ok ? r.value.join("+") : r.error);\n',
                    'const r = parseAmount(list[i], `items[${i}]`);',
                    [('[1,2,3]', "1+2+3"),
                     ('[1,"x",3]', "items[1] must be a number")],
                    hints=["Pass the element and a path built from the index.",
                           "A template literal makes the path: `items[${i}]`."],
                    difficulty="Medium"),
                _diagnose("tscourse-w15-va-d1", "Reading before checking",
                          "TS18046: 'raw' is of type 'unknown'.",
                          _LINE +
                          'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                          'function isEntry(v: unknown): v is Entry {\n'
                          '  if (typeof v !== "object" || v === null) {\n    return false;\n  }\n'
                          '  const o = v as Record<string, unknown>;\n'
                          '  return typeof o.desc === "string" && typeof o.cents === "number";\n}\n'
                          'const raw: unknown = JSON.parse(line);\n'
                          'console.log(`${raw.desc} ${raw.cents}`);\n',
                          _LINE +
                          'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                          'function isEntry(v: unknown): v is Entry {\n'
                          '  if (typeof v !== "object" || v === null) {\n    return false;\n  }\n'
                          '  const o = v as Record<string, unknown>;\n'
                          '  return typeof o.desc === "string" && typeof o.cents === "number";\n}\n'
                          'const raw: unknown = JSON.parse(line);\n'
                          'console.log(isEntry(raw) ? `${raw.desc} ${raw.cents}` : "invalid");\n',
                          [('{"desc":"coffee","cents":325}', "coffee 325"),
                           ('42', "invalid")],
                          hints=["The guard is already written — it just is not being called.",
                                 "Use it as the condition, and the value narrows inside.",
                                 "Handle the other branch too: print \"invalid\"."],
                          difficulty="Medium"),
                _fix("tscourse-w15-va-fix1", "Fix the guard that only half-checked",
                     "`isEntry` promises `v is Entry` but never checks `cents`, and the compiler believes it — so a `cents` of `\"lots\"` is accepted and `.toFixed` crashes. It should print `3.25` then `invalid`.",
                     _LINE +
                     'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                     'function isEntry(v: unknown): v is Entry {\n'
                     '  if (typeof v !== "object" || v === null) {\n    return false;\n  }\n'
                     '  const o = v as Record<string, unknown>;\n'
                     '  return typeof o.desc === "string";\n}\n'
                     'const raw: unknown = JSON.parse(line);\n'
                     'console.log(isEntry(raw) ? (raw.cents / 100).toFixed(2) : "invalid");\n',
                     _LINE +
                     'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                     'function isEntry(v: unknown): v is Entry {\n'
                     '  if (typeof v !== "object" || v === null) {\n    return false;\n  }\n'
                     '  const o = v as Record<string, unknown>;\n'
                     '  return typeof o.desc === "string" && typeof o.cents === "number";\n}\n'
                     'const raw: unknown = JSON.parse(line);\n'
                     'console.log(isEntry(raw) ? (raw.cents / 100).toFixed(2) : "invalid");\n',
                     [('{"desc":"coffee","cents":325}', "3.25"),
                      ('{"desc":"coffee","cents":"lots"}', "invalid")],
                     hints=["A `v is T` predicate is trusted, not verified — the compiler never checks the body.",
                            "The guard claims Entry, so it has to check every member of Entry.",
                            "Add the cents check with &&."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A guard that checks two of three members…",
                   ["is caught by the compiler", "is believed anyway — the predicate is a promise",
                    "is a type error", "narrows partially"], 1,
                   "Keep guards small and obvious."),
                _q("Schema libraries like Zod exist to…",
                   ["replace TypeScript", "generate the runtime check and the type from one declaration",
                    "speed up parsing", "avoid unknown"], 1,
                   "So the two cannot drift."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #15 — load a JSON ledger safely",
        """
Every capstone so far has read input the course itself designed. This one reads a
**JSON file it did not write**, which means every value in it is a claim until
checked.

Input is one JSON document on stdin:

```
{"entries":[{"desc":"coffee","cents":325,"tag":"food"},{"desc":"rent","cents":90000,"tag":"home"}]}
```

Print exactly:

```
Entries:  2
Total:    $903.25
By tag:   food=$3.25, home=$900.00
```

And when anything at all is wrong, print one line naming the problem precisely:

```
Invalid:  entries[0].cents must be a number
```

Build this scaffolding:

```ts
type Result<T> = { ok: true; value: T } | { ok: false; error: string };

interface Entry {
  readonly desc: string;
  readonly cents: number;
  readonly tag: string;
}

function asRecord(v: unknown): Record<string, unknown> | undefined
function parseEntry(v: unknown, where: string): Result<Entry>
function parseLedger(text: string): Result<readonly Entry[]>
```

Rules:

- **`JSON.parse`'s result is annotated `unknown`.** There is no `any` in the file,
  and the only `as` is the earned one inside `asRecord` — after its `typeof` and
  `!== null` check.
- Every failure is a **returned `Result`**, never a thrown error, and every
  message names the path: `entries[2].tag must be a string`.
- The five failures to report, with these exact messages:
  - `not valid JSON` — `JSON.parse` threw
  - `document must be an object`
  - `entries must be an array`
  - `entries[N] must be an object`
  - `entries[N].desc must be a string` (and the same for `cents`/`tag`)
- Check members in the order **desc, cents, tag**, so the first bad one is the one
  reported.
- Use `catch` with **no binding** — the message is fixed, so there is nothing to
  inspect.
- A local mutable accumulator inside a parsing function is fine (week 13's rules
  are about values that escape). The `readonly Entry[]` you return is not.
- `By tag` lists each tag once, alphabetically, with its total.
""",
        _ch("tscourse-w15-capstone", "Budget Buddy #15", "Medium",
            "Write the Result type, the earned-assertion helper, and the two validating parsers.",
            _FS + 'type Result<T> =\n'
            '  | { ok: true; value: T }\n'
            '  | { ok: false; error: string };\n'
            'interface Entry {\n'
            '  readonly desc: string;\n  readonly cents: number;\n  readonly tag: string;\n}\n'
            'function asRecord(v: unknown): Record<string, unknown> | undefined {\n'
            '  if (typeof v !== "object" || v === null) {\n    return undefined;\n  }\n'
            '  return v as Record<string, unknown>;\n}\n'
            'function parseEntry(v: unknown, where: string): Result<Entry> {\n'
            '  const o = asRecord(v);\n'
            '  if (o === undefined) {\n'
            '    return { ok: false, error: `${where} must be an object` };\n  }\n'
            '  if (typeof o.desc !== "string") {\n'
            '    return { ok: false, error: `${where}.desc must be a string` };\n  }\n'
            '  if (typeof o.cents !== "number") {\n'
            '    return { ok: false, error: `${where}.cents must be a number` };\n  }\n'
            '  if (typeof o.tag !== "string") {\n'
            '    return { ok: false, error: `${where}.tag must be a string` };\n  }\n'
            '  return { ok: true, value: { desc: o.desc, cents: o.cents, tag: o.tag } };\n}\n'
            'function parseLedger(text: string): Result<readonly Entry[]> {\n'
            '  let raw: unknown;\n'
            '  try {\n    raw = JSON.parse(text);\n'
            '  } catch {\n'
            '    return { ok: false, error: "not valid JSON" };\n  }\n'
            '  const doc = asRecord(raw);\n'
            '  if (doc === undefined) {\n'
            '    return { ok: false, error: "document must be an object" };\n  }\n'
            '  if (!Array.isArray(doc.entries)) {\n'
            '    return { ok: false, error: "entries must be an array" };\n  }\n'
            '  const list: readonly unknown[] = doc.entries;\n'
            '  const out: Entry[] = [];\n'
            '  for (let i = 0; i < list.length; i = i + 1) {\n'
            '    const r = parseEntry(list[i], `entries[${i}]`);\n'
            '    if (!r.ok) {\n      return r;\n    }\n'
            '    out.push(r.value);\n  }\n'
            '  return { ok: true, value: out };\n}\n'
            'const parsed = parseLedger(fs.readFileSync(0, "utf8"));\n'
            'if (!parsed.ok) {\n'
            '  console.log(`Invalid:  ${parsed.error}`);\n'
            '} else {\n'
            '  const entries = parsed.value;\n'
            '  const tags = entries.map((e) => e.tag).filter((t, i, a) => a.indexOf(t) === i).sort();\n'
            '  const byTag = tags.map((t) => {\n'
            '    const sum = entries.filter((e) => e.tag === t).reduce((s, e) => s + e.cents, 0);\n'
            '    return `${t}=$${(sum / 100).toFixed(2)}`;\n'
            '  });\n'
            '  console.log(`Entries:  ${entries.length}`);\n'
            '  console.log(`Total:    $${(entries.reduce((s, e) => s + e.cents, 0) / 100).toFixed(2)}`);\n'
            '  console.log(`By tag:   ${byTag.join(", ")}`);\n}\n',
            'type Result<T> =\n'
            '  | { ok: true; value: T }\n'
            '  | { ok: false; error: string };\n'
            'interface Entry {\n'
            '  readonly desc: string;\n  readonly cents: number;\n  readonly tag: string;\n}\n'
            'function asRecord(v: unknown): Record<string, unknown> | undefined {\n'
            '  if (typeof v !== "object" || v === null) {\n    return undefined;\n  }\n'
            '  return v as Record<string, unknown>;\n}\n'
            'function parseEntry(v: unknown, where: string): Result<Entry> {\n'
            '  const o = asRecord(v);\n'
            '  if (o === undefined) {\n'
            '    return { ok: false, error: `${where} must be an object` };\n  }\n'
            '  if (typeof o.desc !== "string") {\n'
            '    return { ok: false, error: `${where}.desc must be a string` };\n  }\n'
            '  if (typeof o.cents !== "number") {\n'
            '    return { ok: false, error: `${where}.cents must be a number` };\n  }\n'
            '  if (typeof o.tag !== "string") {\n'
            '    return { ok: false, error: `${where}.tag must be a string` };\n  }\n'
            '  return { ok: true, value: { desc: o.desc, cents: o.cents, tag: o.tag } };\n}\n'
            'function parseLedger(text: string): Result<readonly Entry[]> {\n'
            '  let raw: unknown;\n'
            '  try {\n    raw = JSON.parse(text);\n'
            '  } catch {\n'
            '    return { ok: false, error: "not valid JSON" };\n  }\n'
            '  const doc = asRecord(raw);\n'
            '  if (doc === undefined) {\n'
            '    return { ok: false, error: "document must be an object" };\n  }\n'
            '  if (!Array.isArray(doc.entries)) {\n'
            '    return { ok: false, error: "entries must be an array" };\n  }\n'
            '  const list: readonly unknown[] = doc.entries;\n'
            '  const out: Entry[] = [];\n'
            '  for (let i = 0; i < list.length; i = i + 1) {\n'
            '    const r = parseEntry(list[i], `entries[${i}]`);\n'
            '    if (!r.ok) {\n      return r;\n    }\n'
            '    out.push(r.value);\n  }\n'
            '  return { ok: true, value: out };\n}',
            [('{"entries":[{"desc":"coffee","cents":325,"tag":"food"},{"desc":"rent","cents":90000,"tag":"home"}]}',
              "Entries:  2\nTotal:    $903.25\nBy tag:   food=$3.25, home=$900.00"),
             ('{"entries":[{"desc":"tea","cents":200,"tag":"food"}]}',
              "Entries:  1\nTotal:    $2.00\nBy tag:   food=$2.00"),
             ('{"entries":[{"desc":"coffee","cents":"lots","tag":"food"}]}',
              "Invalid:  entries[0].cents must be a number"),
             ('{"entries":[{"desc":"coffee","cents":325,"tag":"food"},{"desc":"rent","cents":90000}]}',
              "Invalid:  entries[1].tag must be a string"),
             ('{oops',
              "Invalid:  not valid JSON"),
             ('{"entries":"nope"}',
              "Invalid:  entries must be an array"),
             ('42',
              "Invalid:  document must be an object"),
             ('{"entries":[7]}',
              "Invalid:  entries[0] must be an object")],
            hints=["`asRecord` holds the ONLY assertion in the file, and its typeof/null guard is what earns it.",
                   "parseEntry checks desc, then cents, then tag — in that order, so the first bad member is the one reported.",
                   "Build the Entry member by member at the end; a spread would carry any extra JSON keys along (week 14).",
                   "parseLedger wraps JSON.parse in try/catch with NO binding, since the message is fixed.",
                   "`Array.isArray(doc.entries)` narrows to any[], so assign it to a `readonly unknown[]` before reading elements.",
                   "On an element failure, `return r` — the failure member already has the right shape for Result<readonly Entry[]>.",
                   "The local `out: Entry[]` is fine: it never escapes, and what you return is a readonly array."]),
        example_io="Entries:  2\nTotal:    $903.25\nBy tag:   food=$3.25, home=$900.00",
        rubric=["JSON.parse's result is annotated unknown; there is no `any` anywhere",
                "the only `as` is inside asRecord, directly after a typeof and null check",
                "every failure is a returned Result, never a thrown error",
                "error messages name the path, including the array index",
                "members are checked in the order desc, cents, tag",
                "the catch has no binding",
                "the Entry is built member by member rather than spread",
                "By tag lists each tag once, alphabetically"],
        stretch=_ch("tscourse-w15-capstone-stretch", "Budget Buddy #15 (stretch)", "Medium",
                    "Report EVERY bad entry instead of stopping at the first. Collect the failures "
                    "and print them joined with `; ` — so a caller fixing a file sees all the "
                    "problems in one pass.",
                    _FS + 'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };\n'
                    'interface Entry {\n'
                    '  readonly desc: string;\n  readonly cents: number;\n  readonly tag: string;\n}\n'
                    'function asRecord(v: unknown): Record<string, unknown> | undefined {\n'
                    '  if (typeof v !== "object" || v === null) {\n    return undefined;\n  }\n'
                    '  return v as Record<string, unknown>;\n}\n'
                    'function parseEntry(v: unknown, where: string): Result<Entry> {\n'
                    '  const o = asRecord(v);\n'
                    '  if (o === undefined) {\n'
                    '    return { ok: false, error: `${where} must be an object` };\n  }\n'
                    '  if (typeof o.desc !== "string") {\n'
                    '    return { ok: false, error: `${where}.desc must be a string` };\n  }\n'
                    '  if (typeof o.cents !== "number") {\n'
                    '    return { ok: false, error: `${where}.cents must be a number` };\n  }\n'
                    '  if (typeof o.tag !== "string") {\n'
                    '    return { ok: false, error: `${where}.tag must be a string` };\n  }\n'
                    '  return { ok: true, value: { desc: o.desc, cents: o.cents, tag: o.tag } };\n}\n'
                    'function parseAllEntries(list: readonly unknown[]): Result<readonly Entry[]> {\n'
                    '  const out: Entry[] = [];\n'
                    '  const problems: string[] = [];\n'
                    '  for (let i = 0; i < list.length; i = i + 1) {\n'
                    '    const r = parseEntry(list[i], `entries[${i}]`);\n'
                    '    if (r.ok) {\n      out.push(r.value);\n    } else {\n'
                    '      problems.push(r.error);\n    }\n  }\n'
                    '  if (problems.length > 0) {\n'
                    '    return { ok: false, error: problems.join("; ") };\n  }\n'
                    '  return { ok: true, value: out };\n}\n'
                    'const raw: unknown = JSON.parse(fs.readFileSync(0, "utf8"));\n'
                    'const doc = asRecord(raw);\n'
                    'const list: readonly unknown[] =\n'
                    '  doc !== undefined && Array.isArray(doc.entries) ? doc.entries : [];\n'
                    'const parsed = parseAllEntries(list);\n'
                    'if (!parsed.ok) {\n'
                    '  console.log(`Invalid:  ${parsed.error}`);\n'
                    '} else {\n'
                    '  console.log(`Entries:  ${parsed.value.length}`);\n'
                    '  console.log(`Total:    $${(parsed.value.reduce((s, e) => s + e.cents, 0) / 100).toFixed(2)}`);\n}\n',
                    'function parseAllEntries(list: readonly unknown[]): Result<readonly Entry[]> {\n'
                    '  const out: Entry[] = [];\n'
                    '  const problems: string[] = [];\n'
                    '  for (let i = 0; i < list.length; i = i + 1) {\n'
                    '    const r = parseEntry(list[i], `entries[${i}]`);\n'
                    '    if (r.ok) {\n      out.push(r.value);\n    } else {\n'
                    '      problems.push(r.error);\n    }\n  }\n'
                    '  if (problems.length > 0) {\n'
                    '    return { ok: false, error: problems.join("; ") };\n  }\n'
                    '  return { ok: true, value: out };\n}',
                    [('{"entries":[{"desc":"coffee","cents":325,"tag":"food"}]}',
                      "Entries:  1\nTotal:    $3.25"),
                     ('{"entries":[{"desc":"coffee","cents":"lots","tag":"food"},{"desc":"rent","cents":90000}]}',
                      "Invalid:  entries[0].cents must be a number; entries[1].tag must be a string"),
                     ('{"entries":[7,{"desc":"a","cents":1,"tag":"b"}]}',
                      "Invalid:  entries[0] must be an object")],
                    hints=["Keep two accumulators: the entries that parsed, and the messages that did not.",
                           "Do not return early on a failure — record it and carry on to the next element.",
                           "After the loop, report the problems if there are any, otherwise the values.",
                           "Join the messages with a semicolon and a space."]),
    ),
))
