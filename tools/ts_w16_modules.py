# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 16 — modules, tsconfig & declaration files.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# THE STRUCTURAL PROBLEM, AND HOW THIS WEEK ANSWERS IT
#
# TS_ROADMAP called this "the highest structural risk in the course": the judge
# compiles ONE file, so there is no module resolution and no second file to
# import from. Every option was tested against the real checker and the real
# runner before a line was authored, and the results decided the week:
#
#   export const / function / default / { a, b } / type    clean, and RUNS
#   export {} (the marker)                                 clean, and RUNS
#   import * as fs / { readFileSync } / alias / default     clean, and RUNS
#   declare global { var X }  + globalThis.X = …            clean, and RUNS
#   interface declaration merging                           clean, and RUNS
#   ---------------------------------------------------------------------
#   import from "./money.js"       TS2307, and ERR_MODULE_NOT_FOUND at runtime
#   import from "zod"              TS2307
#   namespace N { … }              type-checks, then dies in strip-only mode
#   declare module "leftpad"       TS2664 — cannot be resolved, so unusable
#
# So the week does NOT simulate modules with namespaces. It teaches the real
# thing, judged for real, and is honest about the one part it cannot run:
#
#  1. A file with a top-level `export` **is** a module, and these programs are.
#     Every export exercise is executed code, not a mock-up.
#  2. `import` from another FILE is impossible here — so it is taught through a
#     `diagnose` whose error is the genuine TS2307, and the fix is the one a
#     single-file project really has: declare it here.
#  3. The one module that resolves is `"fs"`, which every program in this course
#     has imported since week 2. All four import forms are taught against it,
#     which makes them real rather than illustrative.
#  4. A multi-file project is simulated with `// ---- money.ts ----` section
#     comments, and lesson 1 says out loud that this is what it is. The
#     capstone is laid out that way and its rubric grades the boundaries.
#  5. `namespace` gets exactly one exercise, graded `judge_mode: "types"` —
#     which is not a workaround but the lesson (decision 5 in TS_ROADMAP): a
#     namespace needs a toolchain that *transforms* TypeScript, and Node,
#     esbuild and `--erasableSyntaxOnly` all refuse it. Week 12 spent this
#     argument against `enum`; here it is against namespaces.
#
# ---------------------------------------------------------------------------
# THE BEST FIND, and it is lesson 5's payload.
#
# A circular import's failure mode can be reproduced EXACTLY in one file, with
# no imports at all:
#
#     function grossOf(cents: number): number {
#       return Math.round(cents * (1 + RATE));   // reads RATE when CALLED
#     }
#     const preview = grossOf(1000);             // …called before RATE exists
#     const RATE = 0.2;
#
# It type-checks clean (a function body is deferred, so the compiler permits the
# forward reference) and then dies at runtime with
# `ReferenceError: Cannot access 'RATE' before initialization` — the same
# temporal-dead-zone error, from the same cause, that a two-file cycle produces.
# Shipped as a `fix`, so the learner watches the mechanism rather than reading
# about it.
#
# ---------------------------------------------------------------------------
# AND THE FLAG THE COURSE HAS BEEN WEARING SINCE WEEK 6.
#
# `noUncheckedIndexedAccess` has been on since week 6 (INDEXED_FROM_WEEK) and
# has never been named. Lesson 7 names it, which is the one place in the course
# where the *configuration* is visible in every exercise the learner has already
# done. Note the code: element access has no name to quote, so it is **TS2532
# ("Object is possibly 'undefined'")**, not the TS18048 you would guess — the
# same asymmetry TS_ROADMAP's table records.
# ---------------------------------------------------------------------------

# --- Week 16 --------------------------------------------------------------
_WEEKS.append(_week(
    16, 4, _M4,
    "Modules, tsconfig & Declaration Files",
    "Split a program across files, then control how the whole project is checked: import/export, compiler strictness, and .d.ts files for code that came without types.",
    """
For fifteen weeks you have written *programs*. This week is about **projects**:
how code is divided into files, how those files find each other, and how the
whole thing is checked.

## Three questions, one week

* **What is a file's public surface?** `export` — and, more usefully, what you
  *don't* export.
* **Who decides what compiles?** `tsconfig.json`. Every error you have seen in
  this course exists because a flag is on, and this week names them.
* **What about code that has no types at all?** A `.d.ts` file and `declare` —
  the one place where you write types for somebody else's JavaScript.

## An honest note about the exercises

The judge compiles **one file**, so there is no second file to import from. That
constraint shapes the week, and rather than pretend otherwise:

* Every `export` you write here is real. A file with a top-level `export` **is**
  a module — these programs run as ES modules, and lesson 1 proves it.
* Every `import` form is taught against `"fs"`, the module every program in this
  course has imported since week 2.
* A multi-file project is simulated with section comments:

```ts
// ---- money.ts ----
export function toMoney(cents: number): string { … }

// ---- main.ts ----
console.log(toMoney(325));
```

  In a real project those are two files and the second line of `main.ts` is an
  `import`. Here they are one file with a line drawn on it. Everything else
  about the boundary — what is exported, what stays private, what depends on
  what — is identical, and that is the part worth practising.
* One exercise is graded by the type-checker alone, because `namespace` cannot
  run at all. That is the lesson, not a dodge.

⏱️ Budget about **eight hours**.
""",
    objectives=[
        "Say what makes a file a module rather than a script, and why `export {}` exists",
        "Export values, functions and types, and rename on the way out",
        "Say what a default export costs, and why named exports are the usual advice",
        "Read the four import forms and say what each binds",
        "Explain why a barrel file is convenient and how it invites a cycle",
        "Recognise the temporal-dead-zone crash a circular import produces",
        "Name the flags `strict` turns on, and the error each one produces",
        "Say what `noUncheckedIndexedAccess` does — the flag this course has used since week 6",
        "Write a `.d.ts`-style `declare` for a global that arrives from outside your code",
        "Merge a declaration to extend a type you do not own",
        "Say why `namespace` and `enum` need a build step that `import`/`export` do not",
    ],
    why="Everything before this week was one program. Real work is a repository: dozens of files, a config that decides what counts as an error, and at least one dependency that shipped without types. Knowing where a boundary goes — and being able to read a project's `tsconfig.json` and say what it will and will not catch — is most of what separates someone who writes TypeScript from someone who can be dropped into an existing codebase.",
    est_minutes=480,
    glossary=[
        _gloss("module", "A file with a top-level `import` or `export`. Its top-level names are private to it."),
        _gloss("script", "A file with neither. Its top-level names go into the global scope."),
        _gloss("export {}", "The empty export — the marker that makes an otherwise-script file a module."),
        _gloss("named export", "`export const x` / `export { x }` — imported by the exact name, or renamed with `as`."),
        _gloss("default export", "`export default v` — one per module, named by whoever imports it."),
        _gloss("export type", "Exports a type only. Erased completely, so it cannot be imported as a value."),
        _gloss("namespace import", "`import * as fs from \"fs\"` — binds the whole module as one object."),
        _gloss("import alias", "`import { readFileSync as read }` — renames on the way in."),
        _gloss("import type", "Marks an import as types-only, so the build can erase the whole statement."),
        _gloss("barrel file", "An `index.ts` that re-exports a folder's public surface, so callers import one path."),
        _gloss("circular import", "A depends on B and B on A. Legal, and the reason for most 'undefined is not a function' at start-up."),
        _gloss("temporal dead zone", "The window before a `const`/`let` is initialised. Reading it there throws ReferenceError."),
        _gloss("tsconfig.json", "The file that decides what the compiler checks, and how modules are resolved."),
        _gloss("strict", "One flag that turns on the whole family below. Always on in this course."),
        _gloss("noImplicitAny", "A parameter with no annotation and no inferable type is an error (TS7006)."),
        _gloss("strictNullChecks", "`null` and `undefined` are their own types, not members of every type."),
        _gloss("strictPropertyInitialization", "A class field must be assigned by the end of the constructor (TS2564)."),
        _gloss("useUnknownInCatchVariables", "`catch (e)` gives `unknown` rather than `any`."),
        _gloss("noUncheckedIndexedAccess", "`xs[i]` is `T | undefined`. On in this course since week 6."),
        _gloss("noImplicitReturns", "Every code path must return, if any of them does (TS2366)."),
        _gloss("exactOptionalPropertyTypes", "`x?: T` stops accepting an explicit `undefined`."),
        _gloss("erasableSyntaxOnly", "Forbids syntax that needs a transform — `enum`, `namespace`, parameter properties."),
        _gloss("declaration file (.d.ts)", "Types with no implementation. What ships alongside compiled JavaScript."),
        _gloss("declare", "\"This exists; here is its type.\" No value is emitted."),
        _gloss("declare global", "Adds to the global scope from inside a module — how you type a host-supplied global."),
        _gloss("declaration merging", "Two `interface` declarations of the same name combine into one."),
        _gloss("ambient", "Declared without being defined — the types for code that arrives from somewhere else."),
        _gloss("namespace", "The pre-modules way to group names. Needs a build step, so modern code does not use it."),
    ],
    cheatsheet="""
```ts
// ---- what makes a module ------------------------------------------------
export const RATE = 0.2;        // a top-level export ⇒ this file is a MODULE
export {};                       // …and this is how you say so with nothing to export
// in a module, a top-level `const` is NOT a global:
console.log("RATE" in globalThis);   // false

// ---- the public surface -------------------------------------------------
function round2(n: number): number { … }        // private to the file
export function share(t: number, n: number) { … }  // public
export { round2 as roundTo2 };                   // rename on the way out
export interface Entry { desc: string; }         // a type, exported
export type { Entry };                           // types only, erased entirely

// ---- default vs named ---------------------------------------------------
export default function total(xs: readonly number[]): number { … }
// one per module; the importer chooses the name, so nothing keeps them honest.
// Prefer NAMED exports: they rename-refactor, auto-import and grep.

// ---- the four import forms ----------------------------------------------
import * as fs from "fs";                    // namespace: the module as an object
import { readFileSync } from "fs";           // named
import { readFileSync as read } from "fs";   // named + alias
import fs from "fs";                         // default (synthesised for CJS)
import type { Entry } from "./entry.js";     // types only — erased at build time

// ---- barrels, and the cycle they invite ---------------------------------
// index.ts:   export { toMoney } from "./money.js";
//             export { parse } from "./parse.js";
// …then parse.ts imports from "./index.js" and the cycle is closed.
// The crash it produces, reproduced without any imports at all:
function grossOf(c: number): number { return Math.round(c * (1 + RATE)); }
const preview = grossOf(1000);   // ❌ ReferenceError: Cannot access 'RATE'…
const RATE = 0.2;                //    …before initialization

// ---- tsconfig, the flags that produced every error in this course -------
// "strict": true  turns on, among others:
//   noImplicitAny                TS7006  parameter implicitly has an 'any' type
//   strictNullChecks             TS2322  Type 'null' is not assignable to 'string'
//   strictPropertyInitialization TS2564  Property has no initializer
//   useUnknownInCatchVariables   TS18046 'err' is of type 'unknown'
// and separately (on here since week 6):
//   noUncheckedIndexedAccess     TS2532  Object is possibly 'undefined'
const xs: number[] = [1];
xs[0].toFixed(1);          // ❌ TS2532 — element access has no name to blame
(xs[0] ?? 0).toFixed(1);   // ✅
const [first = 0] = xs;    // ✅ a default in the destructure
xs.at(0) ?? 0;             // ✅ .at() is typed `T | undefined` regardless

// ---- typing what came without types ------------------------------------
declare global {
  var CURRENCY: string;             // "the host supplies this"
}
export {};
globalThis.CURRENCY = "USD";        // …and here the host does
console.log(CURRENCY);

interface Opts { level: number; }
interface Opts { tag: string; }     // declaration MERGING — one Opts, two members

declare function slugify(s: string): string;   // no body: TS1183 if you add one
namespace Money { export const RATE = 0.2; }   // legal TypeScript, unrunnable JS
```
""",
    self_check=[
        "Can you say what makes a file a module, and what changes about its top-level names?",
        "Can you say why `export {}` is ever written?",
        "Can you export a function under a different name than it has locally?",
        "Can you say what a default export leaves up to the importer?",
        "Can you name the four import forms and say what each binds?",
        "Can you say what a barrel file buys, and what it risks?",
        "Can you explain the ReferenceError a circular import produces, in terms of initialisation order?",
        "Can you name four flags `strict` turns on, and one error each produces?",
        "Can you say which flag has been making `xs[0]` possibly-undefined all course?",
        "Can you list three ways to satisfy that flag, and say which needs no assertion?",
        "Can you write a `declare global` for a value the host supplies?",
        "Can you add a member to an interface you do not own?",
        "Can you say why `namespace` and `enum` cannot run in this judge?",
    ],
    review=[
        _q("A file is a module when…",
           ["it is named .ts", "it has a top-level import or export", "it has a class",
            "tsconfig says so"], 1,
           "That is the whole rule."),
        _q("A top-level `const` in a module is…",
           ["global", "private to the file", "exported", "readonly"], 1,
           "Module scope. In a script it would be global."),
        _q("`export {}` at the bottom of a file…",
           ["exports everything", "makes the file a module and exports nothing",
            "is a syntax error", "clears the exports"], 1,
           "The marker, for a file that has nothing to export."),
        _q("`export { withTax as gross }` creates…",
           ["a local `gross`", "a public name `gross` for the local `withTax`",
            "two functions", "an alias both sides can use"], 1,
           "The alias is visible to importers only."),
        _q("How many default exports may a module have?",
           ["as many as you like", "exactly one", "one per type", "none"], 1,
           "TS2323 if you write two."),
        _q("The usual advice is to prefer…",
           ["default exports", "named exports — they rename-refactor and auto-import",
            "namespaces", "neither"], 1,
           "A default export's name is chosen by the caller."),
        _q("`import * as fs from \"fs\"` binds…",
           ["one function", "the whole module as an object", "the default export",
            "a type"], 1,
           "A namespace import."),
        _q("`import type { Entry } from \"./entry.js\"` guarantees…",
           ["the file is loaded at runtime", "the statement is erased — no runtime import at all",
            "Entry is a value", "nothing"], 1,
           "Types-only, so the build can drop it."),
        _q("A barrel file is…",
           ["a big module", "an index that re-exports a folder's public surface",
            "a test file", "a config"], 1,
           "Convenient, and the easiest way to create a cycle."),
        _q("A circular import usually shows up as…",
           ["a compile error", "a runtime ReferenceError or an undefined member at start-up",
            "nothing", "a type error"], 1,
           "The modules are legal; the initialisation order is not."),
        _q("`function f() { return RATE; } const x = f(); const RATE = 1;` does what?",
           ["prints 1", "throws ReferenceError: Cannot access 'RATE' before initialization",
            "fails to compile", "prints undefined"], 1,
           "The body runs before the declaration is initialised — the temporal dead zone."),
        _q("TS7006 (\"implicitly has an 'any' type\") comes from…",
           ["strictNullChecks", "noImplicitAny", "noUncheckedIndexedAccess",
            "noImplicitReturns"], 1,
           "An unannotated parameter with nothing to infer from."),
        _q("Which flag makes `xs[0]` have type `number | undefined`?",
           ["strictNullChecks", "noUncheckedIndexedAccess", "strict", "exactOptionalPropertyTypes"], 1,
           "On in this course since week 6, and finally named."),
        _q("`xs[0].toFixed(1)` under that flag reports…",
           ["TS18048 on xs[0]", "TS2532, 'Object is possibly undefined'", "nothing",
            "TS7006"], 1,
           "An element access has no name to quote, so it is the unnamed form."),
        _q("The fix that needs no assertion at all is…",
           ["xs[0]!", "a default: `const [first = 0] = xs`", "as number", "any"], 1,
           "A guard, a `??` or a destructuring default — never a `!`."),
        _q("A `.d.ts` file contains…",
           ["compiled JavaScript", "types with no implementation", "tests", "config"], 1,
           "What ships beside somebody's compiled JS."),
        _q("`declare function f(s: string): string { return s; }` is…",
           ["fine", "TS1183 — an implementation cannot be declared in an ambient context",
            "a type error", "a module"], 1,
           "`declare` means 'no body, trust me'."),
        _q("Two `interface Opts` declarations in one file…",
           ["conflict", "merge into one interface with both members",
            "shadow each other", "are a syntax error"], 1,
           "Declaration merging — how you extend a type you do not own."),
        _q("`namespace` is avoided in modern TypeScript because…",
           ["it is deprecated syntax", "it emits code, so it needs a transform that modules do not",
            "it is slow", "it cannot hold types"], 1,
           "Same argument week 12 made against `enum`."),
    ],
    milestone="Budget Buddy stops being a program and becomes a package. The file is laid out as four modules — `money`, `entry`, `report` and an index that states the public surface — with the helpers deliberately left unexported, a currency symbol that arrives from the host through a `declare global`, and a config object checked against the strictness it claims. It is the first week whose deliverable is a *shape* rather than a feature.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w16-module", "Script or module?",
            "One rule decides, and it changes where your names live.",
            """
TypeScript has exactly one rule for this:

> A file with a top-level `import` or `export` is a **module**. A file with
> neither is a **script**.

Nothing else matters — not the extension, not the config, not the folder.

## Why you care

In a **script**, top-level declarations go into the **global** scope. Two scripts
that both declare `const total` collide, and the collision is a compile error in
a project that includes both.

In a **module**, top-level declarations are private to the file. Nothing escapes
unless you `export` it, and nothing arrives unless you `import` it.

```ts
export const apiKey = "local-only";
console.log("apiKey" in globalThis);   // false — module scope, not global
```

That single line is the whole argument for modules, and you can watch it in this
week's first exercises.

## `export {}`

Sometimes a file has nothing to export but must still be a module — usually
because it needs to be excluded from the global scope, or because a
`declare global` block (lesson 8) is only legal inside a module:

```ts
const apiKey = "local-only";
export {};              // "this file is a module." That is all it does.
```

It looks like a trick and it is really just the rule applied literally: an
`export` is present, therefore this is a module.

## Modules are file-level, and only file-level

```ts
function makeRate(): number {
  export const RATE = 0.2;
  // ❌ TS1184: Modifiers cannot appear here.
  return RATE;
}
```

An export is part of a file's interface, so it can only be written where the file
itself is — at the top level. Not in a function, not in a block, not in an `if`.

## Module code runs once, top to bottom

The first time a module is imported, its top-level code runs. Every import after
that gets the same already-initialised module — it is not re-run. That is why a
module-level `const` is a singleton shared by every importer, which is
occasionally exactly what you want and is otherwise the bug in lesson 2's last
exercise.

## And what a module is *not*

```ts
const fs = require("fs");    // ❌ TS2591: Cannot find name 'require'
```

`require` is CommonJS — the older module system, still everywhere in Node code
written before about 2020. This course, and modern TypeScript, use `import`. The
two are not interchangeable and the error is worth recognising, because the
answer to "why does `require` not work here?" is "because this file is an ES
module".

> ⚠️ **Common mistakes:** expecting a top-level `const` in a module to be visible
> to another file; writing `export` inside a function; and assuming a file is a
> module because it is TypeScript.
""",
            warmup=[
                _q("A file with no import and no export is…",
                   ["a module", "a script — its top-level names are global", "invalid",
                    "a namespace"], 1,
                   "One rule, applied literally."),
                _q("In a module, a top-level `const total = 1` is…",
                   ["a global", "private to that file", "exported", "readonly"], 1,
                   "Nothing escapes without `export`."),
                _q("`export {}` does what?",
                   ["exports every name", "marks the file as a module, exporting nothing",
                    "deletes the exports", "is invalid"], 1,
                   "The marker."),
                _q("`export const x = 1` inside a function is…",
                   ["fine", "TS1184 — modifiers cannot appear here", "a global",
                    "a closure"], 1,
                   "Exports live at file level."),
            ],
            exercises=[
                _ex("tscourse-w16-mod-1", "Make it a module",
                    "Give the rate a public name, so this file has a surface other files could use.",
                    'export const RATE = 0.2;\n'
                    'console.log(`rate ${RATE}`);\n',
                    'export const RATE = 0.2;', [("", "rate 0.2")],
                    hints=["One keyword in front of the declaration.",
                           "Write export const RATE = 0.2;"]),
                _ex("tscourse-w16-mod-2", "A module, and nothing exported",
                    "Make this file a module without giving it a public surface, then prove the key never reached the global scope.",
                    'const apiKey = "local-only";\n'
                    'export {};\n'
                    'console.log(`${apiKey} ${"apiKey" in globalThis}`);\n',
                    'export {};', [("", "local-only false")],
                    hints=["The empty export is two characters of braces after the keyword.",
                           "Write export {};"],
                    difficulty="Easy"),
                _ex("tscourse-w16-mod-3", "Two files, one judge",
                    "This is how the week writes a multi-file project: a section comment where the file boundary would be. Export the helper the `main.ts` section below depends on.",
                    '// ---- money.ts ----\n'
                    'export function toMoney(cents: number): string {\n'
                    '  return `$${(cents / 100).toFixed(2)}`;\n}\n'
                    '// ---- main.ts ----\n'
                    'console.log(toMoney(325));\n',
                    'export function toMoney(cents: number): string {',
                    [("", "$3.25")],
                    hints=["In a real project the second section would begin with an import of this name.",
                           "Write export function toMoney(cents: number): string {"],
                    difficulty="Easy"),
                _diagnose("tscourse-w16-mod-d1", "An export where it cannot go",
                          "TS1184: Modifiers cannot appear here.",
                          'function makeRate(): number {\n'
                          '  export const RATE = 0.2;\n'
                          '  return RATE;\n}\n'
                          'console.log(makeRate());\n',
                          'export const RATE = 0.2;\n'
                          'function makeRate(): number {\n'
                          '  return RATE;\n}\n'
                          'console.log(makeRate());\n',
                          [("", "0.2")],
                          hints=["An export is part of the FILE's interface, so it has to be written at file level.",
                                 "Move the declaration out of the function and leave the function reading it.",
                                 "Declare `export const RATE = 0.2;` above `makeRate`."],
                          difficulty="Easy"),
                _diagnose("tscourse-w16-mod-d2", "The second file that does not exist",
                          "TS2307: Cannot find module './money.js' or its corresponding type declarations.",
                          'import { toMoney } from "./money.js";\n'
                          'console.log(toMoney(325));\n',
                          '// ---- money.ts ----\n'
                          'export function toMoney(cents: number): string {\n'
                          '  return `$${(cents / 100).toFixed(2)}`;\n}\n'
                          '// ---- main.ts ----\n'
                          'console.log(toMoney(325));\n',
                          [("", "$3.25")],
                          hints=["The judge compiles exactly one file, so there is no `money.ts` to resolve.",
                                 "Do what a single-file project does: declare the function here, in its own section.",
                                 "Keep the section comment, export `toMoney`, and call it below."],
                          difficulty="Medium"),
                _fix("tscourse-w16-mod-fix1", "Fix the CommonJS import",
                     "This was copied out of an older Node codebase. `require` is CommonJS; an ES module has no such function, so the compiler cannot even find the name.",
                     'const fs = require("fs");\n'
                     'const line: string = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(line.toUpperCase());\n',
                     'import * as fs from "fs";\n'
                     'const line: string = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(line.toUpperCase());\n',
                     [("coffee", "COFFEE"), ("flat white", "FLAT WHITE")],
                     hints=["TS2591: Cannot find name 'require'. It is not that the module is missing — the FUNCTION is.",
                            "Use the form every program in this course has used since week 2.",
                            'Write import * as fs from "fs";'],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Module top-level code runs…",
                   ["on every import", "once, the first time the module is loaded", "never",
                    "twice"], 1,
                   "Which is what makes module state a singleton."),
                _q("`require` fails in these programs because…",
                   ["Node is too old", "this file is an ES module, and `require` is CommonJS",
                    "fs is missing", "it needs a type"], 1,
                   "Two different module systems."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w16-export", "The public surface",
            "What you export is an API. What you don't is the freedom to change your mind.",
            """
Exporting is not a formality — it is the decision about what the rest of the
codebase is allowed to depend on. Every exported name is a promise; every
unexported one is a thing you can rename at 5pm on a Friday.

## The forms

```ts
export const RATE = 0.2;                      // on the declaration
export function share(t: number, n: number) { … }
export interface Entry { desc: string; }
export type Cents = number;

const secret = "…";
function round2(n: number) { … }
export { secret, round2 };                     // a list, usually at the bottom
```

Both forms are identical to importers. The inline form keeps the marker next to
the thing; the list form gives you one place to read the whole surface, which is
why a lot of codebases prefer it.

## Renaming on the way out

```ts
function withTaxCents(cents: number): number { … }
export { withTaxCents as gross };
```

Internally the honest, awkward name; externally the name that reads well at call
sites. Note what this does **not** do: it creates no local `gross`. The alias
exists only for importers, which catches people out the first time.

## Types are exported too

```ts
export interface Entry { readonly desc: string; }   // a type, exported
export type { Entry };                              // types-ONLY export
```

`export type { … }` guarantees the export is erased entirely — nobody can
accidentally import it as a value, and a build tool can drop the statement
without looking anything up. When a file exports both types and values, marking
the type exports this way is a small, free kindness to whoever configures the
build.

## The surface is the smaller half

A good module exports two or three names and keeps ten to itself:

```ts
function round2(n: number): number {                 // private: an implementation detail
  return Math.round(n * 100) / 100;
}
export function share(total: number, people: number): number {   // public: the point
  return round2(total / people);
}
```

If `round2` were exported, someone would import it, and it would become
impossible to delete. That is the whole cost of an over-wide surface, and it is
paid later, by somebody else.

## Module state is shared state

Top-level code runs once, so a module-level `let` or array is a **singleton**
that every importer sees:

```ts
const lines: string[] = [];                     // created ONCE
export function report(items: readonly string[]): string {
  for (const it of items) { lines.push(it); }
  return lines.join(",");
}
```

Call it twice and the second answer contains the first call's data. Sometimes
that is a cache and it is deliberate. Far more often it is the bug in this
lesson's last exercise.

> ⚠️ **Common mistakes:** exporting everything "in case"; expecting
> `export { x as y }` to give you a local `y`; and keeping mutable state at module
> level without meaning to.
""",
            warmup=[
                _q("`export { withTax as gross }` gives the current file…",
                   ["a local `gross`", "nothing new — the alias is for importers only",
                    "two functions", "a type"], 1,
                   "It renames on the way out."),
                _q("`export type { Entry }` guarantees…",
                   ["Entry is a value", "the export is types-only and fully erased",
                    "Entry is default", "nothing"], 1,
                   "Nobody can import it as a value."),
                _q("A helper you do NOT export is…",
                   ["unusable", "free to rename or delete later", "global", "slower"], 1,
                   "That freedom is the point of a small surface."),
                _q("A module-level array shared by every importer is…",
                   ["impossible", "a singleton — one array for the whole program",
                    "copied per import", "readonly"], 1,
                   "Top-level code runs once."),
            ],
            exercises=[
                _ex("tscourse-w16-ex-1", "Public function, private helper",
                    "Export the function callers need, and leave the rounding helper private.",
                    'function round2(n: number): number {\n'
                    '  return Math.round(n * 100) / 100;\n}\n'
                    'export function share(total: number, people: number): number {\n'
                    '  return round2(total / people);\n}\n'
                    'console.log(share(100, 3));\n',
                    'export function share(total: number, people: number): number {',
                    [("", "33.33")],
                    hints=["Only one of these two functions belongs to the outside world.",
                           "Write export function share(total: number, people: number): number {"]),
                _ex("tscourse-w16-ex-2", "State the surface in one place",
                    "Rather than marking each declaration, list the module's public names at the bottom.",
                    'const RATE = 0.2;\n'
                    'function withTax(cents: number): number {\n'
                    '  return Math.round(cents * (1 + RATE));\n}\n'
                    'export { RATE, withTax };\n'
                    'console.log(withTax(1000));\n',
                    'export { RATE, withTax };', [("", "1200")],
                    hints=["One export statement, naming both.",
                           "Write export { RATE, withTax };"],
                    difficulty="Easy"),
                _ex("tscourse-w16-ex-3", "A better name on the outside",
                    "Keep the precise local name, but publish it as `gross`.",
                    'function withTaxCents(cents: number): number {\n'
                    '  return Math.round(cents * 1.2);\n}\n'
                    'export { withTaxCents as gross };\n'
                    'console.log(withTaxCents(1000));\n',
                    'export { withTaxCents as gross };', [("", "1200")],
                    hints=["The `as` goes inside the braces, local name first.",
                           "Note the call below still uses the LOCAL name — the alias is for importers.",
                           "Write export { withTaxCents as gross };"],
                    difficulty="Medium"),
                _ex("tscourse-w16-ex-4", "Export the type as well",
                    "A module's surface includes the types callers need to talk to it. Export the alias.",
                    'export interface Entry {\n'
                    '  readonly desc: string;\n  readonly cents: number;\n}\n'
                    'export type Cents = number;\n'
                    'const e: Entry = { desc: "coffee", cents: 325 };\n'
                    'const c: Cents = e.cents;\n'
                    'console.log(`${e.desc} ${c}`);\n',
                    'export type Cents = number;', [("", "coffee 325")],
                    hints=["Same keyword as a value export, in front of the type alias.",
                           "Write export type Cents = number;"],
                    difficulty="Easy"),
                _ex("tscourse-w16-ex-5", "Types only, and erased",
                    "Export `Entry` in the form that cannot be imported as a value.",
                    'interface Entry {\n'
                    '  readonly desc: string;\n}\n'
                    'export type { Entry };\n'
                    'const e: Entry = { desc: "tea" };\n'
                    'console.log(e.desc);\n',
                    'export type { Entry };', [("", "tea")],
                    hints=["The `type` keyword goes between `export` and the braces.",
                           "Write export type { Entry };"],
                    difficulty="Medium"),
                _diagnose("tscourse-w16-ex-d1", "The export list that lies",
                          "TS2552: Cannot find name 'totals'. Did you mean 'total'?",
                          'const total = 325;\n'
                          'export { totals };\n'
                          'console.log(total);\n',
                          'const total = 325;\n'
                          'export { total };\n'
                          'console.log(total);\n',
                          [("", "325")],
                          hints=["An export list names local bindings, so a typo in it is an unresolved name.",
                                 "The compiler has already guessed what you meant.",
                                 "Write export { total };"],
                          difficulty="Easy"),
                _fix("tscourse-w16-ex-fix1", "Fix the report that remembers",
                     "`report` is called twice and the second call answers `a,b,c` instead of `c`. The accumulator is module state — created once, shared by every call — when it should be per-call.",
                     '// ---- report.ts ----\n'
                     'const lines: string[] = [];\n'
                     'export function report(items: readonly string[]): string {\n'
                     '  for (const it of items) {\n'
                     '    lines.push(it);\n  }\n'
                     '  return lines.join(",");\n}\n'
                     '// ---- main.ts ----\n'
                     'console.log(report(["a", "b"]));\n'
                     'console.log(report(["c"]));\n',
                     '// ---- report.ts ----\n'
                     'export function report(items: readonly string[]): string {\n'
                     '  const lines: string[] = [];\n'
                     '  for (const it of items) {\n'
                     '    lines.push(it);\n  }\n'
                     '  return lines.join(",");\n}\n'
                     '// ---- main.ts ----\n'
                     'console.log(report(["a", "b"]));\n'
                     'console.log(report(["c"]));\n',
                     [("", "a,b\nc")],
                     hints=["Top-level code runs once, so that array is created once for the whole program.",
                            "The accumulator belongs to the CALL, not to the module.",
                            "Move the declaration inside the function."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The cost of exporting a helper you did not need to export is…",
                   ["performance", "somebody imports it, and now you cannot change it",
                    "a type error", "nothing"], 1,
                   "An export is a promise."),
                _q("Two calls to a function that pushes into a module-level array…",
                   ["are independent", "share the array — the second sees the first's data",
                    "reset it", "throw"], 1,
                   "Module state is a singleton."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w16-default", "Default exports, and why named ones usually win",
            "One per module, named by the caller.",
            """
A module may have one **default** export:

```ts
export default function total(cents: readonly number[]): number {
  return cents.reduce((s, c) => s + c, 0);
}
```

and the importer picks its name:

```ts
import total from "./total.js";     // or `sum`, or `addUp`, or `t`
```

## Why that is a problem

The name is chosen at every call site, independently. So:

* **Renaming does not propagate.** Rename the function and nothing else changes,
  because nothing else used the name.
* **Auto-import guesses.** Your editor can offer a named export by name; for a
  default it has to invent one from the filename.
* **Grep stops working.** Searching for `total(` finds the call sites of a named
  export. With a default, half the codebase calls it something else.
* **Re-exporting is clumsy.** `export { default as total } from "./total.js"` is
  the barrel line for a default export, which is nobody's favourite syntax.

Named exports have none of these problems, which is why most style guides —
including the TypeScript team's own for the compiler — prefer them. Defaults earn
their place where a module genuinely *is* one thing: a React component, a
configuration object, a single class.

## Mixing them

Legal, and common:

```ts
export const RATE = 0.2;
export default function gross(cents: number): number {
  return Math.round(cents * (1 + RATE));
}
```

## Two errors worth recognising

**Two defaults** — the module cannot decide what it is:

```ts
export default function a(): number { return 1; }
export default function b(): number { return 2; }
// ❌ TS2323: Cannot redeclare exported variable 'default'.
```

**A default that is evaluated too early.** `export default <expression>` runs
where it sits, so exporting a `const` declared below it reads a binding that does
not exist yet:

```ts
export default helper;
const helper = (n: number): number => n * 2;
// ❌ TS2448: Block-scoped variable 'helper' used before its declaration.
```

A `function` declaration would have hoisted and been fine; a `const` arrow does
not. This is the same initialisation-order hazard lesson 5 is about, in
miniature.

> ⚠️ **Common mistakes:** a default export whose name differs everywhere;
> assuming `export default` hoists; and reaching for a default because the module
> has only one function *today*.
""",
            warmup=[
                _q("How many defaults may one module export?",
                   ["any number", "one", "one per type", "zero"], 1,
                   "TS2323 for a second."),
                _q("Who names a default export?",
                   ["the module", "whoever imports it", "tsconfig", "the compiler"], 1,
                   "Which is the root of every objection to them."),
                _q("`export default helper;` above `const helper = …` is…",
                   ["fine", "TS2448 — used before its declaration", "hoisted", "a type error"], 1,
                   "`const` does not hoist into usable existence."),
                _q("Named exports are usually preferred because…",
                   ["they are faster", "they rename-refactor, auto-import and grep",
                    "they are newer", "defaults are deprecated"], 1,
                   "All four reasons are about tooling and change."),
            ],
            exercises=[
                _ex("tscourse-w16-def-1", "One thing, exported by default",
                    "This module is a single function. Export it as the default.",
                    'export default function total(cents: readonly number[]): number {\n'
                    '  return cents.reduce((s, c) => s + c, 0);\n}\n'
                    'console.log(total([100, 225]));\n',
                    'export default function total(cents: readonly number[]): number {',
                    [("", "325")],
                    hints=["Two keywords before `function`.",
                           "Write export default function total(cents: readonly number[]): number {"]),
                _ex("tscourse-w16-def-2", "A module that is an object",
                    "Publish the whole helper object as this module's default export.",
                    'const money = {\n'
                    '  toMoney(cents: number): string {\n'
                    '    return `$${(cents / 100).toFixed(2)}`;\n  },\n'
                    '};\n'
                    'export default money;\n'
                    'console.log(money.toMoney(325));\n',
                    'export default money;', [("", "$3.25")],
                    hints=["The default can be any expression — here, the name of the object.",
                           "Write export default money;"],
                    difficulty="Easy"),
                _ex("tscourse-w16-def-3", "A default and a named export together",
                    "Keep `RATE` a named export and make the function the default.",
                    'export const RATE = 0.2;\n'
                    'export default function gross(cents: number): number {\n'
                    '  return Math.round(cents * (1 + RATE));\n}\n'
                    'console.log(`${RATE} ${gross(1000)}`);\n',
                    'export default function gross(cents: number): number {',
                    [("", "0.2 1200")],
                    hints=["Both may appear in one module.",
                           "Write export default function gross(cents: number): number {"],
                    difficulty="Easy"),
                _diagnose("tscourse-w16-def-d1", "Two defaults",
                          "TS2323: Cannot redeclare exported variable 'default'.",
                          'export default function a(): number {\n  return 1;\n}\n'
                          'export default function b(): number {\n  return 2;\n}\n'
                          'console.log(a() + b());\n',
                          'export default function a(): number {\n  return 1;\n}\n'
                          'export function b(): number {\n  return 2;\n}\n'
                          'console.log(a() + b());\n',
                          [("", "3")],
                          hints=["A module has one default, so the second declaration is redeclaring it.",
                                 "Keep one default and publish the other under its own name.",
                                 "Make `b` a plain named export."],
                          difficulty="Easy"),
                _diagnose("tscourse-w16-def-d2", "A default exported too early",
                          "TS2448: Block-scoped variable 'helper' used before its declaration.",
                          'export default helper;\n'
                          'const helper = (n: number): number => n * 2;\n'
                          'console.log(helper(2));\n',
                          'const helper = (n: number): number => n * 2;\n'
                          'export default helper;\n'
                          'console.log(helper(2));\n',
                          [("", "4")],
                          hints=["`export default <expression>` is evaluated where it is written.",
                                 "A `const` arrow is not usable above its own declaration.",
                                 "Move the export below the declaration."],
                          difficulty="Medium"),
            ],
            quiz=[
                _q("`export { default as total } from \"./total.js\"` is…",
                   ["invalid", "how a barrel re-exports a default export", "a type import",
                    "two exports"], 1,
                   "Clumsy, which is part of the argument."),
                _q("A default export is a good fit when…",
                   ["always", "the module genuinely is one thing — a component, a config, a class",
                    "never", "there are many exports"], 1,
                   "Otherwise prefer named."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w16-import", "Reading an import",
            "Four forms, and what each one binds.",
            """
Every program in this course begins with an import, and it has never been
explained:

```ts
import * as fs from "fs";
```

Here are the four forms, all of them against `"fs"` — the one module these
programs can actually resolve.

## Namespace import

```ts
import * as fs from "fs";
fs.readFileSync(0, "utf8");
```

Binds the **whole module** as one object. Good when you want the module's name at
the call site (`path.join`, `fs.readFileSync`) as documentation.

## Named import

```ts
import { readFileSync } from "fs";
readFileSync(0, "utf8");
```

Binds exactly the names you list. This is the form to reach for: it says what the
file depends on, and a bundler can drop everything you did not name.

## Named import with an alias

```ts
import { readFileSync as read } from "fs";
read(0, "utf8");
```

For a name that collides, or one that is long enough to hurt at every call site.

## Default import

```ts
import fs from "fs";
fs.readFileSync(0, "utf8");
```

Binds the module's **default** export. `"fs"` is CommonJS and has no ES default,
so what you get here is a *synthesised* one — the whole `module.exports` object,
courtesy of the interop rules (`esModuleInterop`/`allowSyntheticDefaultImports`).
It works, it is what most Node code written in TypeScript does, and the thing to
notice is that the binding is an **object**, not a function:

```ts
import readFileSync from "fs";
readFileSync(0, "utf8");
// ❌ TS2349: This expression is not callable.
//            Type 'typeof import("fs")' has no call signatures.
```

The name you chose says "function"; the thing you got is the module.

## `import type`

```ts
import type { Entry } from "./entry.js";
import { type Entry, parse } from "./entry.js";   // inline form
```

Marks the import as **types-only**, so the build erases the whole statement and
loads nothing at runtime. Two reasons it matters: it prevents an
import-for-types-only from dragging a module's side effects into your bundle, and
under `verbatimModuleSyntax` (lesson 6) it is *required*, because that flag
forbids the compiler from guessing which imports were types.

## The import that cannot work here

```ts
import { toMoney } from "./money.js";
// ❌ TS2307: Cannot find module './money.js' …
```

There is no second file. In a real project this is the line that ties the project
together; in this judge it is the boundary of what a single file can be, and
lesson 1's section comments are how the week works around it.

> ⚠️ **Common mistakes:** a default import named as though it were the function;
> forgetting the extension in a project that needs one (`./money.js`, even from
> `money.ts`); and importing a whole module for one type.
""",
            warmup=[
                _q("`import * as fs from \"fs\"` binds…",
                   ["one function", "the module as an object", "the default", "a type"], 1,
                   "A namespace import."),
                _q("`import { readFileSync as read } from \"fs\"` binds…",
                   ["both names", "one name, `read`", "the module", "nothing"], 1,
                   "An alias renames on the way in."),
                _q("`import fs from \"fs\"` on a CommonJS module gives…",
                   ["an error", "a synthesised default — the whole module object",
                    "one function", "undefined"], 1,
                   "The interop rules."),
                _q("`import type { Entry } from \"./e.js\"` at runtime…",
                   ["loads e.js", "loads nothing — the statement is erased", "throws",
                    "loads types"], 1,
                   "Types-only."),
            ],
            exercises=[
                _ex("tscourse-w16-imp-1", "Name what you need",
                    "Import only the function this program uses, then read stdin with it.",
                    'import { readFileSync } from "fs";\n'
                    'const line = readFileSync(0, "utf8").trim();\n'
                    'console.log(line.length);\n',
                    'import { readFileSync } from "fs";',
                    [("coffee", "6"), ("flat white", "10")],
                    hints=["A named import lists the bindings inside braces.",
                           'Write import { readFileSync } from "fs";'],
                    difficulty="Easy"),
                _ex("tscourse-w16-imp-2", "Rename on the way in",
                    "Import `readFileSync` under the shorter local name `read`.",
                    'import { readFileSync as read } from "fs";\n'
                    'const line = read(0, "utf8").trim();\n'
                    'console.log(line.toUpperCase());\n',
                    'import { readFileSync as read } from "fs";',
                    [("coffee", "COFFEE")],
                    hints=["The `as` goes inside the braces: exported name first, local name second.",
                           'Write import { readFileSync as read } from "fs";'],
                    difficulty="Easy"),
                _ex("tscourse-w16-imp-3", "The form you have used all course",
                    "Bind the whole module as `fs`, the way every program since week 2 has.",
                    'import * as fs from "fs";\n'
                    'const words = fs.readFileSync(0, "utf8").trim().split(" ");\n'
                    'console.log(words.length);\n',
                    'import * as fs from "fs";',
                    [("a b c", "3"), ("one", "1")],
                    hints=["A star, then the local name for the whole module.",
                           'Write import * as fs from "fs";'],
                    difficulty="Easy"),
                _ex("tscourse-w16-imp-4", "The synthesised default",
                    "Import the module through its default binding and read stdin from it.",
                    'import fs from "fs";\n'
                    'const line = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(`[${line}]`);\n',
                    'import fs from "fs";', [("coffee", "[coffee]")],
                    hints=["No braces and no star — just the name you want the default bound to.",
                           'Write import fs from "fs";'],
                    difficulty="Medium"),
                _diagnose("tscourse-w16-imp-d1", "The default that is not a function",
                          "TS2349: This expression is not callable. Type 'typeof import(\"fs\")' has no call signatures.",
                          'import readFileSync from "fs";\n'
                          'console.log(readFileSync(0, "utf8").trim());\n',
                          'import { readFileSync } from "fs";\n'
                          'console.log(readFileSync(0, "utf8").trim());\n',
                          [("coffee", "coffee")],
                          hints=["The name says function; the form asks for the module's default, which is the whole module object.",
                                 "You wanted one member of the module, not the module.",
                                 "Add the braces that make it a named import."],
                          difficulty="Medium"),
                _diagnose("tscourse-w16-imp-d2", "A dependency that is not installed",
                          "TS2307: Cannot find module 'zod' or its corresponding type declarations.",
                          'import { parseCents } from "zod";\n'
                          'console.log(parseCents("325"));\n',
                          'function parseCents(text: string): number {\n'
                          '  const n = Number(text);\n'
                          '  return Number.isFinite(n) ? n : 0;\n}\n'
                          'console.log(parseCents("325"));\n',
                          [("", "325")],
                          hints=["The judge has no package directory, so nothing outside this file resolves.",
                                 "Write the three lines the import was standing in for.",
                                 "`Number.isFinite` decides whether the parse worked."],
                          difficulty="Medium"),
            ],
            quiz=[
                _q("A named import is usually preferred over a namespace import because…",
                   ["it is shorter", "it states exactly what the file depends on, and can be tree-shaken",
                    "it is faster to type", "namespaces are deprecated"], 1,
                   "The dependency list is the documentation."),
                _q("`verbatimModuleSyntax` requires `import type` because…",
                   ["it is stricter about names", "the compiler is no longer allowed to guess which imports were types",
                    "types are slower", "it bans imports"], 1,
                   "What you wrote is what is emitted."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w16-shape", "Barrels, cycles and initialisation order",
            "The convenient thing, and the crash it invites.",
            """
## The barrel

A folder of modules, and one `index.ts` that states the folder's public surface:

```ts
// money/index.ts
export { toMoney, toCents } from "./convert.js";
export { RATE, withTax } from "./tax.js";
export type { Cents } from "./types.js";
```

Callers then write `import { toMoney } from "./money/index.js"` — one path
instead of three, and the folder's internals stay free to move. That is a real
benefit and barrels are everywhere.

## The cycle

The cost arrives the first time something *inside* the folder imports the
barrel — usually because it needed a type from a sibling and the barrel was the
obvious path:

```
convert.ts  →  index.ts  →  tax.ts  →  index.ts  →  …
```

A cycle is not an error. The module system handles it by giving one of the two a
**partially initialised** version of the other, and the result depends entirely on
which file was loaded first.

## What a cycle actually looks like when it breaks

You get one of two failures at start-up, both a long way from their cause:

* `TypeError: x is not a function` — the binding existed but was still
  `undefined` when your code read it.
* `ReferenceError: Cannot access 'X' before initialization` — the binding was a
  `const`, and reading a `const` before its initialiser has run throws.

That second one is the **temporal dead zone**, and it has nothing to do with
modules. You can reproduce a cycle's exact crash in one file:

```ts
function grossOf(cents: number): number {
  return Math.round(cents * (1 + RATE));    // reads RATE when CALLED
}
const preview = grossOf(1000);              // …and it is called right here
const RATE = 0.2;                           // …before this line has run
```

It type-checks **clean** — a function body is deferred, so the compiler is right
not to complain — and then dies:

```
ReferenceError: Cannot access 'RATE' before initialization
```

Once you can see that, a circular import stops being mysterious: some file's
top-level code ran before the `const` it depended on was initialised. Same
mechanism, further apart.

## The fixes, in order of preference

1. **Move the top-level call below what it needs.** Most "cycles" are really one
   eager line in the wrong place.
2. **Do not import the barrel from inside it.** Import the sibling directly
   (`./tax.js`, not `./index.js`). This single rule removes most cycles.
3. **Make the dependency lazy.** A function that reads the value when called,
   rather than a `const` computed at load time.
4. **Import only the type** — `import type` is erased, so it cannot create a
   runtime cycle at all.
5. **Extract the shared thing** into a third module both can depend on.

## Layout, briefly

The shape that survives: leaves at the bottom (types, pure helpers), the things
that combine them above, one entry point at the top, and **no arrows pointing
back down the stack**. This week's capstone is laid out that way on purpose.

> ⚠️ **Common mistakes:** importing your own barrel; computing something at module
> load time that did not need to be; and reading a crash at start-up as a bug in
> the file that crashed rather than in the load order.
""",
            warmup=[
                _q("A barrel file is…",
                   ["a big module", "an index that re-exports a folder's public surface",
                    "a bundle", "a test"], 1,
                   "One import path for callers."),
                _q("A circular import is…",
                   ["a compile error", "legal — one side just gets a partially initialised module",
                    "impossible", "always fatal"], 1,
                   "Which is what makes it hard to debug."),
                _q("`ReferenceError: Cannot access 'X' before initialization` means…",
                   ["X does not exist", "X was read before its declaration ran — the temporal dead zone",
                    "X is null", "a type error"], 1,
                   "The `const` was not initialised yet."),
                _q("The single rule that removes most cycles is…",
                   ["use default exports", "never import your own barrel from inside the folder",
                    "avoid types", "use namespaces"], 1,
                   "Import the sibling directly."),
            ],
            exercises=[
                _ex("tscourse-w16-shape-1", "State the folder's surface",
                    "Gather this section's public names into one export list, the way a barrel does.",
                    '// ---- convert.ts ----\n'
                    'function toMoney(cents: number): string {\n'
                    '  return `$${(cents / 100).toFixed(2)}`;\n}\n'
                    'function toCents(money: string): number {\n'
                    '  return Math.round(Number(money.replace("$", "")) * 100);\n}\n'
                    '// ---- index.ts ----\n'
                    'export { toMoney, toCents };\n'
                    '// ---- main.ts ----\n'
                    'console.log(`${toMoney(325)} ${toCents("$4.50")}`);\n',
                    'export { toMoney, toCents };', [("", "$3.25 450")],
                    hints=["The index states the surface and declares nothing of its own.",
                           "Write export { toMoney, toCents };"],
                    difficulty="Easy"),
                _ex("tscourse-w16-shape-2", "Make the dependency lazy",
                    "The eager `const` is the problem. Compute the preview inside a function, so it reads the rate when called rather than when the module loads.",
                    'function grossOf(cents: number): number {\n'
                    '  return Math.round(cents * (1 + RATE));\n}\n'
                    'function preview(): string {\n'
                    '  return `${grossOf(1000)} ${grossOf(500)}`;\n}\n'
                    'const RATE = 0.2;\n'
                    'console.log(preview());\n',
                    'function preview(): string {', [("", "1200 600")],
                    hints=["A function body runs when it is called, and the call below is after `RATE`.",
                           "Write function preview(): string {"],
                    difficulty="Medium"),
                _ex("tscourse-w16-shape-3", "Order the layers",
                    "Put the declaration where the eager call can already see it.",
                    'const RATE = 0.2;\n'
                    'function grossOf(cents: number): number {\n'
                    '  return Math.round(cents * (1 + RATE));\n}\n'
                    'const preview = grossOf(1000);\n'
                    'console.log(preview);\n',
                    'const RATE = 0.2;', [("", "1200")],
                    hints=["The eager line is `const preview = grossOf(1000)`, so everything it reads must be initialised above it.",
                           "Write const RATE = 0.2; as the first line."],
                    difficulty="Easy"),
                _fix("tscourse-w16-shape-fix1", "Fix the crash a cycle would give you",
                     "This compiles cleanly and then dies with `ReferenceError: Cannot access 'RATE' before initialization`. It is the exact failure a circular import produces: top-level code ran before the `const` it depends on was initialised. Move the eager call, not the function.",
                     'function grossOf(cents: number): number {\n'
                     '  return Math.round(cents * (1 + RATE));\n}\n'
                     'const preview = grossOf(1000);\n'
                     'const RATE = 0.2;\n'
                     'console.log(`${preview} ${grossOf(500)}`);\n',
                     'function grossOf(cents: number): number {\n'
                     '  return Math.round(cents * (1 + RATE));\n}\n'
                     'const RATE = 0.2;\n'
                     'const preview = grossOf(1000);\n'
                     'console.log(`${preview} ${grossOf(500)}`);\n',
                     [("", "1200 600")],
                     hints=["The function is fine — its body is deferred, which is why the compiler said nothing.",
                            "The problem is the line that CALLS it, which sits above the declaration it needs.",
                            "Swap the two `const` lines."],
                     difficulty="Medium"),
                # Deliberately the COMPILE-time twin of fix1, and the contrast is the
                # lesson: here the initialiser reads `TAGS` directly, so the compiler
                # sees the use-before-declaration (TS2448). In fix1 the read happens
                # inside a deferred function body, where it cannot.
                _fix("tscourse-w16-shape-fix2", "Fix the eager table",
                     "`LABELS` is built at load time from `TAGS`, which is declared below it. Unlike the previous exercise the compiler catches this one — TS2448 — because the initialiser reads `TAGS` directly rather than from inside a function body it has to defer. Same mistake, caught much earlier.",
                     'const LABELS: readonly string[] = TAGS.map((t) => t.toUpperCase());\n'
                     'const TAGS: readonly string[] = ["food", "home"];\n'
                     'console.log(LABELS.join(","));\n',
                     'const TAGS: readonly string[] = ["food", "home"];\n'
                     'const LABELS: readonly string[] = TAGS.map((t) => t.toUpperCase());\n'
                     'console.log(LABELS.join(","));\n',
                     [("", "FOOD,HOME")],
                     hints=["A derived table cannot be built above the table it derives from.",
                            "There is no function here to defer anything — the only fix is order.",
                            "Declare `TAGS` first."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("`import type` cannot create a runtime cycle because…",
                   ["types are fast", "the statement is erased, so nothing is loaded",
                    "it is checked first", "it is lazy"], 1,
                   "Nothing to load, nothing to cycle."),
                _q("A module-level `const X = f()` where f reads another module's const is…",
                   ["safe", "an initialisation-order dependency, and the usual cause of the crash",
                    "lazy", "a type error"], 1,
                   "Eager top-level work is the risk."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w16-tsconfig", "The config that decides what compiles",
            "Every error in this course exists because a flag is on.",
            """
`tsconfig.json` is the project's settings file. It answers two questions: **what
counts as an error**, and **how are modules resolved**. You have been programming
under one all course without seeing it.

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "erasableSyntaxOnly": true,
    "verbatimModuleSyntax": true,
    "noEmit": true
  }
}
```

## `strict` is a family, not a flag

`"strict": true` turns on about a dozen checks. The four you have met most:

| flag | what it does | the error |
|---|---|---|
| `noImplicitAny` | a parameter with nothing to infer from must be annotated | **TS7006** |
| `strictNullChecks` | `null`/`undefined` are their own types | **TS2322** |
| `strictPropertyInitialization` | a field must be assigned by the end of the constructor | **TS2564** |
| `useUnknownInCatchVariables` | `catch (e)` is `unknown`, not `any` | **TS18046** |

Also in the family: `strictFunctionTypes` (week 12's parameter variance),
`strictBindCallApply`, `alwaysStrict`, `noImplicitThis`.

**Turning `strict` off is not a smaller version of TypeScript** — it is a
different language, in which `undefined` is a member of every type. Every
guarantee in weeks 9-15 depends on it.

## The flags outside the family, worth knowing

* **`noUncheckedIndexedAccess`** — `xs[i]` is `T | undefined`. On in this course
  since week 6, and lesson 7 is about it.
* **`exactOptionalPropertyTypes`** — `x?: T` stops accepting an explicit
  `undefined`, separating "absent" from "present but empty" (week 15, lesson 2).
* **`noImplicitReturns`** — if any path returns, every path must:
  `function f(n: number): string { if (n > 0) { return "up"; } }` is **TS2366**.
* **`noUnusedLocals` / `noUnusedParameters`** — tidiness, enforced.
* **`erasableSyntaxOnly`** — forbids syntax that needs a transform: `enum`,
  `namespace`, parameter properties. This judge behaves as though it were on,
  because Node *strips* types rather than compiling them.
* **`verbatimModuleSyntax`** — import and export statements are emitted exactly
  as written, so a types-only import must say `import type`.

## Reading a project's config is a skill

Given the file above you can predict what the codebase will and will not catch
before reading a line of it: no implicit `any`, every absence handled, every
index checked, no enums, no namespaces, imports that mean what they say. Given a
config with `"strict": false` you can predict the opposite, and the review
comments you are about to write.

> ⚠️ **Common mistakes:** assuming `strict` covers `noUncheckedIndexedAccess` (it
> does not); turning a flag off to make an error go away; and reading an error
> code without asking which flag produced it.
""",
            warmup=[
                _q("`\"strict\": true` is…",
                   ["one check", "a family of about a dozen checks", "a lint rule", "a target"], 1,
                   "Including noImplicitAny and strictNullChecks."),
                _q("TS7006 comes from…",
                   ["strictNullChecks", "noImplicitAny", "noImplicitReturns",
                    "noUncheckedIndexedAccess"], 1,
                   "An unannotated parameter."),
                _q("Is `noUncheckedIndexedAccess` part of `strict`?",
                   ["yes", "no — it must be turned on separately", "only in ES2022", "it is a lint"], 1,
                   "A common and expensive assumption."),
                _q("`erasableSyntaxOnly` forbids…",
                   ["all types", "syntax that needs a transform: enum, namespace, parameter properties",
                    "imports", "classes"], 1,
                   "Exactly what Node's type stripping cannot run."),
            ],
            exercises=[
                _ex("tscourse-w16-cfg-1", "Type the config you are running under",
                    "Describe the two flags this course uses, then check the object against that type without widening it.",
                    'interface Strictness {\n'
                    '  readonly strict: boolean;\n'
                    '  readonly noUncheckedIndexedAccess: boolean;\n}\n'
                    'const config = {\n'
                    '  strict: true,\n'
                    '  noUncheckedIndexedAccess: true,\n'
                    '} satisfies Strictness;\n'
                    'console.log(`${Object.keys(config).length} ${config.strict}`);\n',
                    '} satisfies Strictness;', [("", "2 true")],
                    hints=["Week 12's operator: check the literal against the type while keeping its exact members.",
                           "Write } satisfies Strictness;"],
                    difficulty="Medium"),
                _ex("tscourse-w16-cfg-2", "Satisfy noImplicitAny",
                    "Annotate the parameter the compiler cannot infer.",
                    'function shout(word: string): string {\n'
                    '  return word.toUpperCase();\n}\n'
                    'console.log(shout("hi"));\n',
                    'function shout(word: string): string {', [("", "HI")],
                    hints=["Nothing at this call site can tell the compiler what `word` is.",
                           "Write function shout(word: string): string {"],
                    difficulty="Easy"),
                _ex("tscourse-w16-cfg-3", "Satisfy noImplicitReturns",
                    "Give the function a return on every path, not just the interesting one.",
                    'function direction(n: number): string {\n'
                    '  if (n > 0) {\n    return "up";\n  }\n'
                    '  return "down";\n}\n'
                    'console.log(`${direction(1)} ${direction(-1)}`);\n',
                    '  return "down";', [("", "up down")],
                    hints=["The `if` handles one case; the function still has to answer in the other.",
                           'Write return "down"; after the if.'],
                    difficulty="Easy"),
                _diagnose("tscourse-w16-cfg-d1", "Which flag was that?",
                          "TS7006: Parameter 'word' implicitly has an 'any' type.",
                          'function shout(word) {\n'
                          '  return word.toUpperCase();\n}\n'
                          'console.log(shout("hi"));\n',
                          'function shout(word: string): string {\n'
                          '  return word.toUpperCase();\n}\n'
                          'console.log(shout("hi"));\n',
                          [("", "HI")],
                          hints=["`noImplicitAny`, from the `strict` family.",
                                 "A parameter in a standalone function has nothing to be inferred from.",
                                 "Annotate it `string` and the return `string`."],
                          difficulty="Easy"),
                _diagnose("tscourse-w16-cfg-d2", "The absence strictNullChecks refuses",
                          "TS2322: Type 'null' is not assignable to type 'string'.",
                          'let tag: string = "food";\n'
                          'tag = null;\n'
                          'console.log(tag);\n',
                          'let tag: string | null = "food";\n'
                          'tag = null;\n'
                          'console.log(tag ?? "-");\n',
                          [("", "-")],
                          hints=["Under `strictNullChecks`, `string` does not include `null` — which is the whole point of week 15.",
                                 "Either stop assigning null, or say in the type that it can be null.",
                                 "Widen the annotation and supply a fallback when printing."],
                          difficulty="Medium"),
                _diagnose("tscourse-w16-cfg-d3", "A field the constructor forgot",
                          "TS2564: Property 'total' has no initializer and is not definitely assigned in the constructor.",
                          'class Ledger {\n'
                          '  total: number;\n'
                          '  add(n: number): void {\n'
                          '    this.total = n;\n  }\n}\n'
                          'const l = new Ledger();\n'
                          'l.add(5);\n'
                          'console.log(l.total);\n',
                          'class Ledger {\n'
                          '  total: number = 0;\n'
                          '  add(n: number): void {\n'
                          '    this.total = this.total + n;\n  }\n}\n'
                          'const l = new Ledger();\n'
                          'l.add(5);\n'
                          'console.log(l.total);\n',
                          [("", "5")],
                          hints=["`strictPropertyInitialization`: a field must hold something by the time the constructor finishes.",
                                 "Assigning it later in a method is not a guarantee — nothing forces `add` to be called.",
                                 "Give the field an initialiser and make `add` accumulate."],
                          difficulty="Medium"),
                _fix("tscourse-w16-cfg-fix1", "Fix it without turning the flag off",
                     "The team's first instinct was to annotate the parameter `any`, which silences the error and switches checking off for everything `word` touches — including the misspelled method below. Type it properly instead.",
                     'function shout(word: any): string {\n'
                     '  return word.toUpperCse();\n}\n'
                     'console.log(shout("hi"));\n',
                     'function shout(word: string): string {\n'
                     '  return word.toUpperCase();\n}\n'
                     'console.log(shout("hi"));\n',
                     [("", "HI")],
                     hints=["`any` did not fix the error, it hid it — and then hid a typo as well.",
                            "The starter crashes at runtime: `word.toUpperCse is not a function`.",
                            "Annotate `string` and let the compiler find the typo for you."],
                     difficulty="Medium"),
                _types("tscourse-w16-cfg-t1", "The flags, as a type",
                       "Describe a strictness preset as a type whose keys are exactly the two flags, each a boolean.",
                       'type Preset = Record<"strict" | "indexed", boolean>;\n'
                       'const course: Preset = { strict: true, indexed: true };\n',
                       'type Preset = Record<"strict" | "indexed", boolean>;',
                       'type _1 = Expect<Equal<Preset, { strict: boolean; indexed: boolean }>>;\n'
                       'type _2 = Expect<Equal<typeof course.indexed, boolean>>;\n',
                       hints=["Week 10's utility, with a union of the two literal keys.",
                              'Write type Preset = Record<"strict" | "indexed", boolean>;'],
                       difficulty="Medium"),
            ],
            quiz=[
                _q("Turning `strict` off gives you…",
                   ["fewer errors, same language", "a different language, in which undefined is a member of every type",
                    "faster builds only", "nothing"], 1,
                   "Weeks 9-15 all depend on it."),
                _q("`verbatimModuleSyntax` means…",
                   ["imports are checked twice", "import/export statements are emitted exactly as written",
                    "no imports", "types are kept"], 1,
                   "So a types-only import must say so."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w16-indexed", "`noUncheckedIndexedAccess`, named at last",
            "The flag you have been using since week 6.",
            """
Ten weeks ago, in week 6, this stopped compiling:

```ts
const nums: number[] = [1, 2, 3];
nums[0].toFixed(1);
// ❌ TS2532: Object is possibly 'undefined'.
```

and the lesson said "arrays are checked here; you will meet the flag later".
This is later. The flag is **`noUncheckedIndexedAccess`**, and it says:

> An index access produces `T | undefined`, because the compiler cannot know the
> index is in range.

## Why it is not part of `strict`

Because it is noisy, and because the noise is honest. `xs[0]` really can be
`undefined` — `[][0]` is — and the type system has no way to know that
`i < xs.length`. Most teams turn it on for new code and regret not having done it
on old code.

It applies to every index access, not just arrays:

```ts
const byTag: Record<string, number> = { food: 325 };
byTag["food"].toFixed(2);       // ❌ TS2532 — the key might not be there
byTag.food.toFixed(2);          // ❌ same thing, dotted
```

## Note the error code

```
TS2532: Object is possibly 'undefined.'
```

not `TS18048: 'nums[0]' is possibly 'undefined'`. TS18048 quotes a **name**, and
an element access has no name to quote — so the unnamed form is what you get.
Worth knowing, because searching for the wrong code finds the wrong advice.

## The four ways to satisfy it

```ts
const xs: readonly number[] = [3, 1, 2];

// 1. A GUARD — the value is narrowed, and nothing is claimed.
const n = xs[0];
if (n !== undefined) { n.toFixed(1); }

// 2. A DEFAULT with ??  — the shortest honest fix.
(xs[0] ?? 0).toFixed(1);

// 3. A DESTRUCTURING DEFAULT — reads best when you want the first few.
const [first = 0, second = 0] = xs;

// 4. .at() — typed `T | undefined` whatever the flags say, so it forces the
//    conversation and supports negative indices.
(xs.at(-1) ?? 0).toFixed(1);
```

And the way that is not a fix:

```ts
xs[0]!.toFixed(1);       // ❌ a claim, checked by nobody (week 15)
```

A `!` is defensible only when a guard directly above it makes the claim true —
and if you have written that guard, you have already narrowed the value and do
not need the `!`.

## The loop shape it changes

The index loop needs one line more than you are used to:

```ts
for (let i = 0; i < nums.length; i = i + 1) {
  const n = nums[i];               // number | undefined
  if (n === undefined) { continue; }
  total = total + n;
}
```

which is why `for … of` is usually better under this flag — the element type of
an iteration is `T`, with no index in sight:

```ts
for (const n of nums) { total = total + n; }     // n is number. No check needed.
```

That is not a workaround; it is the flag telling you that you did not need the
index.

> ⚠️ **Common mistakes:** reaching for `!` because the guard feels obvious;
> assuming `strict` includes this flag; and writing index loops where `for … of`
> would have no absence to handle at all.
""",
            warmup=[
                _q("Under this flag, `xs[0]` has type…",
                   ["number", "number | undefined", "unknown", "never"], 1,
                   "The compiler cannot know the index is in range."),
                _q("The code an element access reports is…",
                   ["TS18048", "TS2532 — there is no name to quote", "TS2322", "TS7006"], 1,
                   "TS18048 quotes a name."),
                _q("Does it apply to `Record<string, number>` lookups?",
                   ["no, only arrays", "yes — any index access", "only with strict", "only tuples"], 1,
                   "The key might not be there either."),
                _q("`for (const n of nums)` gives `n` the type…",
                   ["number | undefined", "number", "unknown", "never"], 1,
                   "No index, no absence."),
            ],
            exercises=[
                _ex("tscourse-w16-idx-1", "Guard, then use",
                    "Bind the element, check it, and only then compare it. No assertion.",
                    _NUMS +
                    'let best = 0;\n'
                    'for (let i = 0; i < nums.length; i = i + 1) {\n'
                    '  const n = nums[i];\n'
                    '  if (n !== undefined && n > best) {\n'
                    '    best = n;\n  }\n}\n'
                    'console.log(best);\n',
                    '  if (n !== undefined && n > best) {',
                    [("3 1 2", "3"), ("5", "5")],
                    hints=["Two conditions: it is there, and it is bigger.",
                           "Write if (n !== undefined && n > best) {"],
                    difficulty="Medium"),
                _ex("tscourse-w16-idx-2", "A default, inline",
                    "Supply a fallback at the point of access, so nothing downstream has an absence to handle.",
                    _NUMS +
                    'const first = nums[0] ?? 0;\n'
                    'console.log(first.toFixed(1));\n',
                    'const first = nums[0] ?? 0;', [("3 1", "3.0"), ("", "0.0")],
                    hints=["The nullish operator, right after the access.",
                           "Write const first = nums[0] ?? 0;"],
                    difficulty="Easy"),
                _ex("tscourse-w16-idx-3", "Defaults in the destructure",
                    "Pull the first two off with defaults, so both are plain numbers.",
                    _NUMS +
                    'const [first = 0, second = 0] = nums;\n'
                    'console.log(first + second);\n',
                    'const [first = 0, second = 0] = nums;',
                    [("3 1 2", "4"), ("7", "7"), ("", "0")],
                    hints=["A default per position, inside the brackets.",
                           "Write const [first = 0, second = 0] = nums;"],
                    difficulty="Medium"),
                _ex("tscourse-w16-idx-4", "The last one, safely",
                    "`.at(-1)` reads from the end, and is `T | undefined` however the flags are set. Give it a fallback.",
                    _NUMS +
                    'const last = nums.at(-1) ?? 0;\n'
                    'console.log(last * 2);\n',
                    'const last = nums.at(-1) ?? 0;', [("3 1 2", "4"), ("5", "10")],
                    hints=["A negative index counts from the end.",
                           "Write const last = nums.at(-1) ?? 0;"],
                    difficulty="Easy"),
                _ex("tscourse-w16-idx-5", "Lose the index entirely",
                    "Rewrite the total as an iteration over elements, where there is no absence to handle at all.",
                    _NUMS +
                    'let total = 0;\n'
                    'for (const n of nums) {\n'
                    '  total = total + n;\n}\n'
                    'console.log(total);\n',
                    'for (const n of nums) {', [("3 1 2", "6"), ("5", "5")],
                    hints=["The flag is about index access, so stop indexing.",
                           "Write for (const n of nums) {"],
                    difficulty="Easy"),
                _predict("tscourse-w16-idx-p1", "What an index really gives you",
                         'const nums: readonly number[] = [3, 1, 2];\n'
                         'const got = nums[0];\n',
                         "got", "number | undefined",
                         why="The flag is on for every week from 6 onwards, this one included.",
                         hints=["The element type, plus the absence the compiler cannot rule out.",
                                "Write number | undefined."]),
                _diagnose("tscourse-w16-idx-d1", "The array access that is not a number",
                          "TS2532: Object is possibly 'undefined'.",
                          'const nums: readonly number[] = [3, 1];\n'
                          'console.log(nums[0].toFixed(1));\n',
                          'const nums: readonly number[] = [3, 1];\n'
                          'console.log((nums[0] ?? 0).toFixed(1));\n',
                          [("", "3.0")],
                          hints=["`noUncheckedIndexedAccess` makes the access `number | undefined`.",
                                 "Supply a fallback before calling a method on it — and mind the parentheses.",
                                 "Write (nums[0] ?? 0).toFixed(1)."],
                          difficulty="Easy"),
                _diagnose("tscourse-w16-idx-d2", "The lookup that might miss",
                          "TS2532: Object is possibly 'undefined'.",
                          'const byTag: Record<string, number> = { food: 325 };\n'
                          'console.log(byTag["home"].toFixed(2));\n',
                          'const byTag: Record<string, number> = { food: 325 };\n'
                          'console.log((byTag["home"] ?? 0).toFixed(2));\n',
                          [("", "0.00")],
                          hints=["A `Record<string, number>` claims nothing about which keys exist.",
                                 "This one genuinely misses — which is the flag earning its keep.",
                                 'Write (byTag["home"] ?? 0).toFixed(2).'],
                          difficulty="Medium"),
                # NOT the shared `_NUMS` prefix: on empty input that one yields `[0]`,
                # because `Number("")` is 0 — so the `!` would never be wrong and the
                # buggy starter would pass. Filtering the empty field out first is what
                # makes the array genuinely empty, and the assertion genuinely false.
                _fix("tscourse-w16-idx-fix1", "Fix the assertion that was a wish",
                     "The `!` silenced the compiler and the program now crashes on an empty ledger: `Cannot read properties of undefined (reading 'toFixed')`. Handle the absence instead of claiming it away.",
                     _FS +
                     'const nums: readonly number[] = fs.readFileSync(0, "utf8")\n'
                     '  .trim()\n'
                     '  .split(" ")\n'
                     '  .filter((s) => s !== "")\n'
                     '  .map(Number);\n'
                     'console.log(nums[0]!.toFixed(1));\n',
                     _FS +
                     'const nums: readonly number[] = fs.readFileSync(0, "utf8")\n'
                     '  .trim()\n'
                     '  .split(" ")\n'
                     '  .filter((s) => s !== "")\n'
                     '  .map(Number);\n'
                     'console.log((nums[0] ?? 0).toFixed(1));\n',
                     [("3 1", "3.0"), ("", "0.0")],
                     hints=["A `!` is a claim about the value, checked by nobody — and on empty input it is false.",
                            "Nothing here guards the access, so there is no assertion to earn.",
                            "Replace the `!` with a `??` fallback."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`xs[0]!` is defensible when…",
                   ["always", "a guard directly above makes the claim true — and then you do not need it",
                    "never", "the array is readonly"], 1,
                   "Which is why it is almost never the answer."),
                _q("Under this flag, an index loop needs…",
                   ["nothing extra", "the element bound and checked, or a `??`", "a cast",
                    "a while loop"], 1,
                   "Or no index at all — `for … of`."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w16-declare", "`.d.ts`, `declare`, and typing what has no types",
            "Types with no implementation, for code that arrived without any.",
            """
Not everything you depend on is TypeScript. A library compiled to JavaScript, a
global the page injected, a value your build tool substituted at compile time —
none of these have types, and all of them need some.

## A declaration file

A `.d.ts` file is **types with no implementation**. It describes what exists
somewhere else:

```ts
// slugify.d.ts
export declare function slugify(input: string): string;
```

Every library that ships compiled JavaScript ships one of these beside it (or in
`@types/…` on npm). Reading them is a genuinely useful skill — a library's `.d.ts`
is the most accurate documentation it has.

## `declare` means "no body"

```ts
declare function slugify(s: string): string;      // ✅ a declaration
declare function slugify(s: string): string {      // ❌ TS1183: An implementation
  return s;                                        //    cannot be declared in
}                                                  //    ambient contexts
```

`declare` emits nothing. You are promising the value exists at runtime, and
nobody checks that promise — which makes it the same kind of claim as `as`, and
worth the same suspicion.

## Typing a host-supplied global

The common real case: a value that is not in your code at all. From inside a
module, `declare global` is how you add it to the global scope:

```ts
declare global {
  var CURRENCY: string;          // `var`, not `const` — globals are declared with var
}
export {};                        // `declare global` is only legal in a MODULE

globalThis.CURRENCY = "USD";      // …in real code, the host does this
console.log(CURRENCY);            // and your code just uses it, typed
```

Two details that trip people up: the block only works inside a module (hence
`export {}`), and members are declared with `var`, because that is what a global
binding is.

## Declaration merging

Two `interface` declarations with the same name **merge**:

```ts
interface Opts { readonly level: number; }
interface Opts { readonly tag: string; }

const o: Opts = { level: 1, tag: "food" };      // both members required
```

This is how you extend a type you do not own — a library's config interface, or a
framework's request object. It is also why `interface` and `type` are not
interchangeable: a `type` alias cannot be reopened, and declares
`TS2300: Duplicate identifier` instead.

Merging refuses to contradict itself:

```ts
interface Opts { level: number; }
interface Opts { level: string; }
// ❌ TS2717: Subsequent property declarations must have the same type.
```

## `namespace`, and why it is not the answer

Before modules, TypeScript grouped names in a `namespace`:

```ts
namespace Money {
  export const RATE = 0.2;
  export function gross(cents: number): number {
    return Math.round(cents * (1 + RATE));
  }
}
Money.gross(1000);
```

It type-checks. It **cannot run here**, and this is the one exercise in the week
graded by the compiler alone:

```
SyntaxError: TypeScript namespace declaration is not supported in strip-only mode
```

A namespace *emits code* — an object and a function wrapper — so it needs a build
step that transforms TypeScript rather than merely stripping it. Node's type
stripping, `esbuild` and `--erasableSyntaxOnly` all refuse it, exactly as they
refuse `enum` (week 12) and parameter properties (week 11).

Namespaces do have one remaining use: in a `.d.ts`, describing a JavaScript
library that really does expose a nested object. In code you write, modules do
the same job with no build step at all.

> ⚠️ **Common mistakes:** giving a `declare` a body; forgetting `export {}` around
> a `declare global`; using `declare` to silence an error about a value that does
> not actually exist at runtime; and reaching for `namespace` to group things when
> a module already does.
""",
            warmup=[
                _q("A `.d.ts` file contains…",
                   ["compiled JS", "types with no implementation", "tests", "config"], 1,
                   "What ships beside a library's JavaScript."),
                _q("`declare function f(): void { }` is…",
                   ["fine", "TS1183 — no implementation in an ambient context", "a module",
                    "hoisted"], 1,
                   "`declare` means no body."),
                _q("`declare global { … }` is legal…",
                   ["anywhere", "only inside a module", "only in a .d.ts", "never"], 1,
                   "Which is why `export {}` turns up next to it."),
                _q("Two `interface Opts` declarations…",
                   ["conflict", "merge", "shadow", "are an error"], 1,
                   "How you extend a type you do not own."),
            ],
            exercises=[
                _ex("tscourse-w16-dec-1", "Type the global the host supplies",
                    "Declare `CURRENCY` as a global string, so the last line can use it without a cast.",
                    'declare global {\n'
                    '  var CURRENCY: string;\n}\n'
                    'export {};\n'
                    'globalThis.CURRENCY = "USD";\n'
                    'console.log(`${CURRENCY} 3.25`);\n',
                    '  var CURRENCY: string;', [("", "USD 3.25")],
                    hints=["A global binding is declared with `var`, whatever your instincts say.",
                           "Write var CURRENCY: string;"],
                    difficulty="Medium"),
                _ex("tscourse-w16-dec-2", "Make the block legal",
                    "`declare global` is only allowed inside a module. Add the one line that makes this file one.",
                    'declare global {\n'
                    '  var CURRENCY: string;\n}\n'
                    'export {};\n'
                    'globalThis.CURRENCY = "EUR";\n'
                    'console.log(CURRENCY);\n',
                    'export {};', [("", "EUR")],
                    hints=["Lesson 1's marker.",
                           "Write export {};"],
                    difficulty="Easy"),
                _ex("tscourse-w16-dec-3", "Declare a function that arrives from outside",
                    "Type the host-supplied `slugify`, then use it.",
                    'declare global {\n'
                    '  var slugify: (s: string) => string;\n}\n'
                    'export {};\n'
                    'globalThis.slugify = (s) => s.trim().toLowerCase().split(" ").join("-");\n'
                    'console.log(slugify("Flat White"));\n',
                    '  var slugify: (s: string) => string;', [("", "flat-white")],
                    hints=["A function type, as the type of a global var.",
                           "Write var slugify: (s: string) => string;"],
                    difficulty="Medium"),
                _ex("tscourse-w16-dec-4", "Extend a type you do not own",
                    "Add a `tag` member to `Opts` by declaring the interface a second time.",
                    '// ---- vendor.d.ts (not ours) ----\n'
                    'interface Opts {\n'
                    '  readonly level: number;\n}\n'
                    '// ---- ours.ts ----\n'
                    'interface Opts {\n'
                    '  readonly tag: string;\n}\n'
                    'const o: Opts = { level: 1, tag: "food" };\n'
                    'console.log(`${o.level} ${o.tag}`);\n',
                    'interface Opts {\n  readonly tag: string;\n}',
                    [("", "1 food")],
                    hints=["Declare it again with only the new member; the two declarations merge.",
                           "Write interface Opts { readonly tag: string; } in the `ours.ts` section."],
                    difficulty="Medium"),
                _diagnose("tscourse-w16-dec-d1", "A declaration with a body",
                          "TS1183: An implementation cannot be declared in ambient contexts.",
                          'declare function slug(s: string): string {\n'
                          '  return s.toLowerCase();\n}\n'
                          'console.log(slug("A"));\n',
                          'function slug(s: string): string {\n'
                          '  return s.toLowerCase();\n}\n'
                          'console.log(slug("A"));\n',
                          [("", "a")],
                          hints=["`declare` says 'this exists elsewhere'. A body says it exists here.",
                                 "You have written the implementation, so it is not ambient at all.",
                                 "Drop the `declare`."],
                          difficulty="Easy"),
                _diagnose("tscourse-w16-dec-d2", "A merge that contradicts itself",
                          "TS2717: Subsequent property declarations must have the same type.",
                          'interface Opts {\n  level: number;\n}\n'
                          'interface Opts {\n  level: string;\n}\n'
                          'const o: Opts = { level: 1 };\n'
                          'console.log(o.level);\n',
                          'interface Opts {\n  level: number;\n}\n'
                          'interface Opts {\n  tag: string;\n}\n'
                          'const o: Opts = { level: 1, tag: "food" };\n'
                          'console.log(`${o.level} ${o.tag}`);\n',
                          [("", "1 food")],
                          hints=["Merging adds members; it cannot re-type one that already exists.",
                                 "Declare a different member in the second interface.",
                                 "Add `tag: string` instead, and supply it in the object."],
                          difficulty="Medium"),
                _fix("tscourse-w16-dec-fix1", "Fix the declaration that promised too much",
                     "`declare` is a promise nobody checks: this one says a global `VERSION` exists, and at runtime nothing ever set it, so the program crashes with `ReferenceError: VERSION is not defined`. Supply the value the declaration claims.",
                     'declare global {\n'
                     '  var VERSION: string;\n}\n'
                     'export {};\n'
                     'console.log(`v${VERSION}`);\n',
                     'declare global {\n'
                     '  var VERSION: string;\n}\n'
                     'export {};\n'
                     'globalThis.VERSION = "1.4.0";\n'
                     'console.log(`v${VERSION}`);\n',
                     [("", "v1.4.0")],
                     hints=["The types were fine — that is exactly the danger.",
                            "A `declare` emits nothing, so something at runtime has to provide the value.",
                            'Assign globalThis.VERSION = "1.4.0"; before it is read.'],
                     difficulty="Medium"),
                _types("tscourse-w16-dec-t1", "The namespace that cannot run",
                       "Group the two names in a `namespace` and give `gross` its signature. This one is graded by "
                       "the compiler alone — a namespace emits an object and a wrapper, so Node's type stripping "
                       "refuses to run it at all. That is the reason modules won.",
                       'namespace Money {\n'
                       '  export const RATE = 0.2;\n'
                       '  export function gross(cents: number): number {\n'
                       '    return Math.round(cents * (1 + RATE));\n  }\n}\n'
                       'type Gross = typeof Money.gross;\n',
                       '  export function gross(cents: number): number {',
                       # `RATE` is a namespace-level `const`, so its type is the LITERAL
                       # 0.2, not `number` — the same widening rule as anywhere else.
                       'type _1 = Expect<Equal<Gross, (cents: number) => number>>;\n'
                       'type _2 = Expect<Equal<typeof Money.RATE, 0.2>>;\n',
                       hints=["Inside a namespace, members still need `export` to be visible outside it.",
                              "The signature takes cents and returns a number.",
                              "Write export function gross(cents: number): number {"],
                       difficulty="Medium"),
                _design("tscourse-w16-dec-des1", "Design the ambient surface",
                        "The host injects one configuration object. Write the global declaration its two members need — "
                        "a currency string and a boolean — so the code below type-checks unchanged.",
                        'declare global {\n'
                        '  var BUDGET: { readonly currency: string; readonly rounding: boolean };\n}\n'
                        'export {};\n'
                        'globalThis.BUDGET = { currency: "USD", rounding: true };\n'
                        'function show(cents: number): string {\n'
                        '  const amount = BUDGET.rounding ? Math.round(cents / 100) : cents / 100;\n'
                        '  return `${BUDGET.currency} ${amount}`;\n}\n'
                        'console.log(show(325));\n',
                        '  var BUDGET: { readonly currency: string; readonly rounding: boolean };',
                        'type _1 = Expect<Equal<typeof BUDGET.currency, string>>;\n'
                        'type _2 = Expect<Equal<typeof BUDGET.rounding, boolean>>;\n',
                        [("", "USD 3")],
                        hints=["One global `var`, whose type is an object with two readonly members.",
                               "`rounding` is used in a condition, and `currency` in a template.",
                               "Write var BUDGET: { readonly currency: string; readonly rounding: boolean };"],
                        difficulty="Medium"),
            ],
            quiz=[
                _q("`declare` is like `as` in that…",
                   ["both are erased", "both are claims nobody checks at runtime", "both are types",
                    "neither compiles"], 1,
                   "A declaration for something that does not exist is a crash in waiting."),
                _q("`namespace` cannot run in this judge because…",
                   ["it is old", "it emits code, and Node only strips types", "it is a type",
                    "it needs an import"], 1,
                   "Same reason as `enum` and parameter properties."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #16 — the project layout",
        """
Budget Buddy has been one program for fifteen weeks. This week it becomes a
**package**: the same behaviour, laid out as four modules with a stated public
surface, plus the two project-level facts this week is about — a global the host
supplies, and a config object that says what it is checked under.

Read a ledger from stdin, one entry per line as `desc cents tag`, and print:

```
Ledger:   2 entries (strict+indexed)
Total:    USD 903.25
Top tag:  home USD 900.00
```

**The layout — four sections, in dependency order, marked with the week's
section comments:**

1. `// ---- config.ts ----` — a `declare global` block for `BUDGET_CURRENCY`
   (a string the host provides), and the `PRESET` config object checked with
   `satisfies` against a `Strictness` interface of `strict` and
   `noUncheckedIndexedAccess` booleans. `label()` turns the preset into the
   `strict+indexed` text.
2. `// ---- money.ts ----` — `toMoney(cents)`, and a private `round2` it uses.
3. `// ---- entry.ts ----` — the `Entry` type and `parseEntry(line)`, returning
   `Entry | undefined` for a line that is not three fields or whose cents are not
   a number.
4. `// ---- report.ts ----` — `report(entries)`, which builds the three lines.
5. `// ---- index.ts ----` — one `export` list naming the public surface, and
   nothing else.
6. `// ---- main.ts ----` — read stdin, parse, print.

**Rules the layout has to keep**, and the rubric is about these rather than the
arithmetic:

* Only `toMoney`, `parseEntry`, `report` and the `Entry` type are exported.
  `round2`, `label` and `PRESET` stay private — they are how it works, not what
  it offers.
* Nothing eager at the top of a section depends on a `const` in a later one, so
  there is no initialisation-order trap (lesson 5).
* Every index access handles its absence — no `!` anywhere (lesson 7).
* A malformed line is skipped, not crashed on.
* Ties for the top tag are broken alphabetically, so the output is deterministic.

Empty input prints `Ledger:   0 entries (strict+indexed)`, a zero total, and
`Top tag:  none`.
""",
        _ch("tscourse-w16-capstone", "Budget Buddy #16", "Hard",
            "Lay the program out as five modules with one export list, a host-supplied "
            "currency and a `satisfies`-checked preset — then report on the ledger.",
            _FS +
            '// ---- config.ts ----\n'
            'declare global {\n'
            '  var BUDGET_CURRENCY: string;\n}\n'
            'interface Strictness {\n'
            '  readonly strict: boolean;\n'
            '  readonly noUncheckedIndexedAccess: boolean;\n}\n'
            'const PRESET = {\n'
            '  strict: true,\n'
            '  noUncheckedIndexedAccess: true,\n'
            '} satisfies Strictness;\n'
            'function label(p: Strictness): string {\n'
            '  return p.noUncheckedIndexedAccess ? "strict+indexed" : "strict";\n}\n'
            '// ---- money.ts ----\n'
            'function round2(n: number): number {\n'
            '  return Math.round(n * 100) / 100;\n}\n'
            'function toMoney(cents: number): string {\n'
            '  return `${BUDGET_CURRENCY} ${round2(cents / 100).toFixed(2)}`;\n}\n'
            '// ---- entry.ts ----\n'
            'interface Entry {\n'
            '  readonly desc: string;\n'
            '  readonly cents: number;\n'
            '  readonly tag: string;\n}\n'
            'function parseEntry(line: string): Entry | undefined {\n'
            '  const parts = line.trim().split(/\\s+/);\n'
            '  if (parts.length !== 3) {\n'
            '    return undefined;\n  }\n'
            '  const desc = parts[0] ?? "";\n'
            '  const cents = Number(parts[1] ?? "");\n'
            '  const tag = parts[2] ?? "";\n'
            '  if (!Number.isFinite(cents)) {\n'
            '    return undefined;\n  }\n'
            '  return { desc, cents, tag };\n}\n'
            '// ---- report.ts ----\n'
            'function report(entries: readonly Entry[]): readonly string[] {\n'
            '  let total = 0;\n'
            '  const byTag: Record<string, number> = {};\n'
            '  for (const e of entries) {\n'
            '    total = total + e.cents;\n'
            '    byTag[e.tag] = (byTag[e.tag] ?? 0) + e.cents;\n  }\n'
            '  let topTag = "none";\n'
            '  let topCents = -1;\n'
            '  for (const tag of Object.keys(byTag).sort()) {\n'
            '    const cents = byTag[tag] ?? 0;\n'
            '    if (cents > topCents) {\n'
            '      topTag = tag;\n      topCents = cents;\n    }\n  }\n'
            '  return [\n'
            '    `Ledger:   ${entries.length} entries (${label(PRESET)})`,\n'
            '    `Total:    ${toMoney(total)}`,\n'
            '    topTag === "none" ? "Top tag:  none" : `Top tag:  ${topTag} ${toMoney(topCents)}`,\n'
            '  ];\n}\n'
            '// ---- index.ts ----\n'
            'export { toMoney, parseEntry, report };\n'
            'export type { Entry };\n'
            '// ---- main.ts ----\n'
            'globalThis.BUDGET_CURRENCY = "USD";\n'
            'const lines = fs.readFileSync(0, "utf8").split("\\n").filter((l) => l.trim() !== "");\n'
            'const entries: Entry[] = [];\n'
            'for (const line of lines) {\n'
            '  const e = parseEntry(line);\n'
            '  if (e !== undefined) {\n'
            '    entries.push(e);\n  }\n}\n'
            'for (const out of report(entries)) {\n'
            '  console.log(out);\n}\n',
            '// ---- report.ts ----\n'
            'function report(entries: readonly Entry[]): readonly string[] {\n'
            '  let total = 0;\n'
            '  const byTag: Record<string, number> = {};\n'
            '  for (const e of entries) {\n'
            '    total = total + e.cents;\n'
            '    byTag[e.tag] = (byTag[e.tag] ?? 0) + e.cents;\n  }\n'
            '  let topTag = "none";\n'
            '  let topCents = -1;\n'
            '  for (const tag of Object.keys(byTag).sort()) {\n'
            '    const cents = byTag[tag] ?? 0;\n'
            '    if (cents > topCents) {\n'
            '      topTag = tag;\n      topCents = cents;\n    }\n  }\n'
            '  return [\n'
            '    `Ledger:   ${entries.length} entries (${label(PRESET)})`,\n'
            '    `Total:    ${toMoney(total)}`,\n'
            '    topTag === "none" ? "Top tag:  none" : `Top tag:  ${topTag} ${toMoney(topCents)}`,\n'
            '  ];\n}\n'
            '// ---- index.ts ----\n'
            'export { toMoney, parseEntry, report };\n'
            'export type { Entry };',
            [("coffee 325 food\nrent 90000 home",
              "Ledger:   2 entries (strict+indexed)\nTotal:    USD 903.25\nTop tag:  home USD 900.00"),
             ("tea 200 food\ncoffee 325 food\nbus 150 travel",
              "Ledger:   3 entries (strict+indexed)\nTotal:    USD 6.75\nTop tag:  food USD 5.25"),
             ("coffee 325 food\noops\nrent 90000 home\ntea notanumber food",
              "Ledger:   2 entries (strict+indexed)\nTotal:    USD 903.25\nTop tag:  home USD 900.00"),
             ("a 100 x\nb 100 y",
              "Ledger:   2 entries (strict+indexed)\nTotal:    USD 2.00\nTop tag:  x USD 1.00"),
             ("", "Ledger:   0 entries (strict+indexed)\nTotal:    USD 0.00\nTop tag:  none")],
            hints=["The report section is the only one left to write: total, a tag map, then the three lines.",
                   "`byTag[tag] ?? 0` on every read — a Record lookup is an absence like any other (lesson 7).",
                   "Sort the tag keys before scanning, and use a strict `>` so the first (alphabetical) tag wins a tie.",
                   "`topCents` starts at -1 so a genuine zero total still beats it.",
                   "The index section exports three values and — separately, with `export type` — the Entry type.",
                   "`label(PRESET)` stays private; only its result appears in the output."]),
        example_io="Ledger:   2 entries (strict+indexed)\nTotal:    USD 903.25\nTop tag:  home USD 900.00",
        rubric=["the file is laid out in dependency order, with the week's section comments",
                "exactly three values and one type are exported — round2, label and PRESET are not",
                "the currency arrives through a `declare global`, not a hard-coded string in money.ts",
                "PRESET is checked with `satisfies`, so its members stay literal",
                "no eager top-level line reads a `const` declared below it",
                "every index access handles its absence; there is no `!` in the file",
                "a malformed line is skipped rather than crashing the run",
                "a tie for the top tag is broken alphabetically"],
        stretch=_ch("tscourse-w16-capstone-stretch", "Budget Buddy #16 (stretch)", "Hard",
                    "Add a `// ---- currency.ts ----` section that keeps a table of symbols and "
                    "makes the host-supplied currency a *lookup* rather than a literal: "
                    "`BUDGET_CURRENCY` now holds a code (`USD`, `EUR`, `JPY`), and `toMoney` prints "
                    "the symbol for it — falling back to the code itself for one it does not know. "
                    "JPY has no minor unit, so its amounts print with no decimals.",
                    _FS +
                    'declare global {\n'
                    '  var BUDGET_CURRENCY: string;\n}\n'
                    '// ---- currency.ts ----\n'
                    'interface Unit {\n'
                    '  readonly symbol: string;\n'
                    '  readonly decimals: number;\n}\n'
                    'const UNITS: Record<string, Unit> = {\n'
                    '  USD: { symbol: "$", decimals: 2 },\n'
                    '  EUR: { symbol: "\\u20ac", decimals: 2 },\n'
                    '  JPY: { symbol: "\\u00a5", decimals: 0 },\n'
                    '};\n'
                    'function unitFor(code: string): Unit {\n'
                    '  return UNITS[code] ?? { symbol: code, decimals: 2 };\n}\n'
                    '// ---- money.ts ----\n'
                    'function toMoney(cents: number): string {\n'
                    '  const unit = unitFor(BUDGET_CURRENCY);\n'
                    '  const amount = unit.decimals === 0 ? cents : cents / 100;\n'
                    '  return `${unit.symbol}${amount.toFixed(unit.decimals)}`;\n}\n'
                    '// ---- main.ts ----\n'
                    'const lines = fs.readFileSync(0, "utf8").split("\\n").filter((l) => l.trim() !== "");\n'
                    'globalThis.BUDGET_CURRENCY = (lines[0] ?? "USD").trim();\n'
                    'let total = 0;\n'
                    'for (const line of lines.slice(1)) {\n'
                    '  const n = Number(line.trim());\n'
                    '  if (Number.isFinite(n)) {\n'
                    '    total = total + n;\n  }\n}\n'
                    'console.log(toMoney(total));\n',
                    '// ---- currency.ts ----\n'
                    'interface Unit {\n'
                    '  readonly symbol: string;\n'
                    '  readonly decimals: number;\n}\n'
                    'const UNITS: Record<string, Unit> = {\n'
                    '  USD: { symbol: "$", decimals: 2 },\n'
                    '  EUR: { symbol: "\\u20ac", decimals: 2 },\n'
                    '  JPY: { symbol: "\\u00a5", decimals: 0 },\n'
                    '};\n'
                    'function unitFor(code: string): Unit {\n'
                    '  return UNITS[code] ?? { symbol: code, decimals: 2 };\n}',
                    [("USD\n325\n90000", "$903.25"),
                     ("JPY\n1200\n300", "¥1500"),
                     ("EUR\n100", "€1.00"),
                     ("GBP\n250", "GBP2.50"),
                     ("USD", "$0.00")],
                    hints=["A `Record<string, Unit>` lookup is an index access, so it needs its `??` fallback.",
                           "The fallback unit uses the code itself as its symbol, with two decimals.",
                           "JPY has no minor unit: its cents ARE yen, so print them with zero decimals.",
                           "The first stdin line is the currency code; the rest are amounts."]),
    ),
))
