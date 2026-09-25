# TypeScript Roadmap — Weeks 22-32

The plan for finishing **TypeScript: Zero to Interview**, the 8-month course in
`tools/typescript_course.py`. Weeks 1-21 ship; weeks 22-32 are one-line
skeletons waiting to be authored.

Unlike [`JAVA_ROADMAP.md`](JAVA_ROADMAP.md), which starts after the basics, this
course starts at *zero* — week 1 is someone's first line of code. That decision
is what makes the back half hard: everything in weeks 22-32 must still obey the
rule that nothing may require syntax a later week teaches.

**Status legend** — ✅ built and shipping · 🚧 partially built · ⬜ planned.

---

## Where it stands

**Built:** weeks 1-21 — **167 lessons, 1,250 judged exercises** (1,235 in lessons
and capstones, 15 in week 1's practice families), twenty Budget Buddy capstones —
**the arc is complete** — the first interview rep, and a full
glossary/cheat-sheet/self-check/review set per week.

| | |
|---|---|
| Content generator | `tools/typescript_course.py` (~690 lines) + one `ts_wNN_*.py` per week |
| Practice | `tools/ts_pNN_practice.py`, optional, one per week |
| Generated seed | `src-tauri/seeds/ts_course.json` |
| UI | `src/pages/Course.tsx` (shared with the Java course), route `/ts-course` |
| Fast verifier | `python tools/verify_ts_course.py --starters` (~10 min) |
| Judge-level verifier | `cd src-tauri && cargo test --test verify_ts_course` (~6 min) |

**Seven exercise kinds** are available. Three are the originals (`drill`, `fix`,
`challenge`); four were added to grade *reading* rather than writing, and weeks
11-32 should use them from the first week rather than retrofitting later:

| kind | the question it asks |
|---|---|
| `predict` | what type does the compiler already infer here? |
| `diagnose` | here is a real `TSnnnn` error — what caused it? |
| `retype` | this runs and its types say nothing; make them honest |
| `design` | write the type first, then the code that satisfies it |

Two grading modes back them: stdout comparison, and `judge_mode: "types"` —
graded on the type-check alone, which is the only way to test a type. Week 10's
`proof` lesson is the working template for the latter.

---

## Five decisions — all taken ✅

These were cheap to settle before authoring and expensive after. None of it is
content; all of it shapes the 22 weeks that follow.

### 1. Split the generator ✅ — done

`typescript_course.py` **was 15,900 lines in one file**. Authored weeks had been
growing steadily:

| W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 | W9 | W10 |
|---|---|---|---|---|---|---|---|---|---|
| 980 | 1,105 | 1,221 | 1,271 | 1,680 | 1,550 | 1,658 | 1,787 | 1,950 | 2,290 |

At that rate (~1,900 lines/week), 22 more weeks would have been **~42,000
lines**, landing the file near 58,000 — not editable, and every week's edit
churning one enormous file.

Now split the way `java_course.py` splits: the parent holds the shared helpers
(`_ex`, `_fix`, `_ch`, `_fn`, `_types`, `_predict`, `_diagnose`, `_retype`,
`_design`, `_week`, `_lesson`, `_fam`), the shared program prefixes (`_FS`,
`_NUMS`, `_WORDS`, `_LINE` — hoisted because more than one week uses them), the
skeletons, the scope lint and the strictness ladder. Each week is one file that
appends to `_WEEKS`:

| | |
|---|---|
| Parent | `tools/typescript_course.py` — **672 lines** (was 15,900) |
| Weeks | `tools/ts_w01_basics.py` … `ts_w10_generics.py`, listed in `_WEEK_FILES` |
| Practice | `tools/ts_pNN_practice.py`, listed in `_PRACTICE_FILES` |

**The split was verified by hash**: the regenerated `ts_course.json` is
byte-identical to the pre-split seed (`03b74f4c…b0582`), which is what proves
the refactor changed nothing but the file layout.

Weeks 11-15 landed this way (`ts_w11_classes.py`, `ts_w12_structural.py`,
`ts_w13_immutability.py`, `ts_w14_utility.py`, `ts_w15_nullsafety.py`, all
appended to `_WEEK_FILES`). Order in that tuple matters — `_WEEKS` is consumed
positionally by the lint and strictness passes.

**One structural gotcha, fixed when week 13 landed:** the month-title constants
used to be defined *after* the `_WEEK_FILES` loop, next to the skeletons. An
authored week in a new month therefore referenced a name that did not exist yet.
`_M4` was moved up then; **`_M5` through `_M8` were moved up when week 17 landed**,
so every remaining week's month title already exists before the loop runs and the
trap cannot fire again.

Batches C and D added `ts_w16_modules.py` (2.2k lines), `ts_w17_async.py` (2.6k),
`ts_w18_stacks.py` (2.2k), `ts_w19_maps.py` (2.1k) and `ts_w20_nodes.py` (2.8k) to
`_WEEK_FILES` — 11.9k lines that would otherwise have gone into one file, which is
exactly what the split was for.

### 2. Where the Budget Buddy arc ends ✅ — decided

Budget Buddy runs unbroken from week 1 ("the receipt line") to week 10 ("a
generic toolkit"), one capstone per week, each genuinely building on the last.
It is the best thing about the course and it does **not** survive contact with
weeks 21-28. A budget app cannot honestly motivate binary search, dynamic
programming or graph traversal, and forcing it to would produce the kind of
contrived capstone the first ten weeks carefully avoid.

**The shape, now recorded in the generator's skeleton header:**

* **Weeks 11-20 — Budget Buddy #11-20.** It keeps earning its place: classes
  give it a real `Ledger`, async gives it a loader, maps give it fast lookup,
  trees give it a category hierarchy. This is its natural ending.
* **Weeks 21-28 — interview reps.** The capstone becomes a timed problem in the
  week's technique, judged the same way. No pretence of a product.
* **Weeks 29-32 — a small typed library.** Build the type-level utilities the
  course has been teaching (`DeepReadonly`, a typed event emitter, a router
  whose paths are parsed by template literal types). This is the natural
  capstone for the advanced-types month and doubles as a portfolio piece.

Each week's `milestone` string is what carries this to the learner, so write the
milestone before the lessons — the milestones are what give the course its
sense of momentum.

### 3. Practice families ✅ — adopted and proven

`CourseWeek.practice` existed in `models.rs` and the shared `Course.tsx` already
rendered it (progress chip, per-family sections, deliberately outside the
completion gate). **The TypeScript course never populated it.** The Java course
does, and gets **775 extra problems** from 155 families.

Now wired: `_fam()` builds a family, `_PRACTICE[n]` collects them, and
`_PRACTICE_FILES` loads one optional file per week *after* the skeletons, so
every week ends up with the key present whether or not it has content.

Two things were extended so practice cannot ship unproven — both were holes
that would have gone unnoticed:

* `_all_programs` now feeds practice through the **scope lint**, so a week-4
  variation cannot reach for a week-8 idea just because it lives in another
  file; and `_all_exercises` feeds it the **strictness ladder**.
* `all_exercises` in `verify_ts_course.rs` now walks practice, so every variant
  is judged by the **real judge** like everything else.

**Proof it works end to end:** `tools/ts_p01_practice.py` ships week 1's first
three families — *Compute, then report* · *Money, to the penny* · *Convert on
purpose* — 15 problems, all verified. The suite went 573 → **588**.

A family is five variations on one pattern, twisting a single dimension at a
time, so no variant is a cold start. It is the right home for repetitive
drilling that would otherwise bloat a lesson, and it must never gate a week.

### 4. Two gaps no week covered ✅ — sequenced

Beyond the six topics resequenced earlier (classes, structural typing,
variance, `satisfies`, `tsconfig`, declaration files), a sweep of all ten
authored weeks plus all 22 skeletons found two more topics that appear
**nowhere** — not in a lesson, not in a program, not in a skeleton theme —
despite both having complete Learn concepts already written:

* **`enum`** (`ts_enums`) → **week 12**, whose goal now ends "…and see why a
  literal union usually beats an enum". The comparison against literal unions
  and `as const` objects *is* the lesson, rather than an aside.
* **`JSON.parse` / `JSON.stringify`** (`ts_json`) → **week 15**, whose goal now
  ends "…then meet untrusted data, where JSON.parse hands back `any` and you
  have to earn a type". The more serious of the two: parsing JSON is *the*
  place `unknown`, type guards and validation stop being theoretical.

Both are in the shipped skeleton goals, so the week that gets authored cannot
quietly drop them.

### 5. Erasable syntax ✅ — found while authoring week 11, and it constrains week 16

The judge runs TypeScript by **stripping** types (Node's type-stripping mode),
not by compiling them. Three constructs are therefore unrunnable, because they
*emit* code rather than merely annotating it:

```
SyntaxError [ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX]:
  TypeScript parameter property is not supported in strip-only mode
  TypeScript enum is not supported in strip-only mode
  TypeScript namespace is not supported in strip-only mode
```

| construct | week that teaches it | how it is graded |
|---|---|---|
| parameter properties | 11, lesson 5 | `judge_mode: "types"` ✅ shipped |
| `enum` | 12, lesson 8 | `judge_mode: "types"` ✅ shipped |
| `namespace` | **16** — unplanned so far | must be `types` too, or omitted |

**This is not a workaround, it is the lesson.** Both shipped weeks name
"erasable syntax" explicitly, and week 12's enum lesson uses it as the *first*
of its three arguments for preferring a literal union — an enum needs a
toolchain that transforms TypeScript, which `--erasableSyntaxOnly`, `esbuild`
and Node all refuse. Week 11 introduces the term so week 12 can spend it.

**What this means for week 16**, whose "compile one file" risk was already
flagged: `namespace` was the obvious way to fake modules in a single file, and
it cannot run. Either type-check-only those exercises or drop namespaces and
teach `import`/`export` purely as reading material. Decide before authoring.

Everything else in weeks 11-12 was checked against the real runner and runs:
`private`/`protected`/`static`/`readonly`, `#private` names, getters and
setters, `implements`, `extends`/`super`, `override`, `abstract`, `satisfies`,
branded intersections, `as const`.

---

## The 22 weeks

Reuse column: the Learn concept whose lesson prose and examples can be adapted.
Concepts are written in Learn's own format, so exercises don't port directly —
the teaching text, worked examples and pitfalls do.

### Month 3 — The Type System, Properly (weeks 11-12) — ✅ **done**

**11. Classes & Objects** ✅ · `tools/ts_w11_classes.py` · 9 lessons, 72
exercises
`w11-why` · `w11-fields` · `w11-methods` · `w11-access` · `w11-params` ·
`w11-accessors` · `w11-implements` · `w11-extends` · `w11-abstract`.
*Capstone:* Budget Buddy #11 — `Expense` + a `Ledger` with a private entries
array; stretch adds `average()`.
Kinds: 45 drill, 13 diagnose, 9 fix, 2 predict, 1 design, 4 type-graded.
**What it cost that the plan didn't predict:** parameter properties cannot run
(decision 5), so lesson 5 grades them by type-check. `protected` was moved from
lesson 4 to lesson 8, because it means nothing until a subclass exists.
Two `fix` exercises are genuine runtime crashes rather than wrong output — a
detached method losing `this`, and a setter that assigns to itself.

**12. Structural Typing, Variance & `satisfies`** ✅ ·
`tools/ts_w12_structural.py` · 8 lessons, 58 exercises
`w12-structural` · `w12-assignable` · `w12-excess` · `w12-fnvariance` ·
`w12-arrays` · `w12-satisfies` · `w12-branded` · `w12-enums`.
*Capstone:* Budget Buddy #12 — branded `Cents`, a `satisfies`-checked budget
table, per-category over/under; stretch adds a second brand, `Percent`.
Kinds: 28 drill, 13 diagnose, 8 fix, 7 predict, 11 type-graded.
**The medium risk was real and this is how it was paid down.** Variance has
almost nothing to print, so the week leans on `diagnose` (13) and `predict` (7)
as planned — but two lessons found genuinely *observable* holes, and those carry
the teaching:
* `w12-assignable` — a wider object keeps its extra key after assignment, so
  `Object.keys` prints `x,y,z` for a two-member type. Annotating does not
  reshape the value.
* `w12-arrays` — `Dog[]` → `Animal[]` → push a plain animal → the `Dog[]` now
  holds a non-dog, printed at runtime. Unsoundness you can watch.
Method bivariance gets the same treatment: a `fix` whose starter compiles and
then throws `v.toUpperCase is not a function`.

### Month 4 — Robust, Real-World Programs (weeks 13-16) — ✅ **done**

**13. Immutability & `readonly`** ✅ · `tools/ts_w13_immutability.py` · 8 lessons,
59 exercises
`w13-why` · `w13-readonly` · `w13-asconst` · `w13-copy` · `w13-shallow` ·
`w13-pure` · `w13-freeze` · `w13-history`.
*Capstone:* Budget Buddy #13 — an immutable ledger with undo; stretch adds a
pure `remove` that `undo` reverses for free.
**The "must deepen, not introduce" constraint held**, and the file's header
records exactly what each earlier week already used (`readonly` in 8 and 11,
`as const` in 9, `readonly T[]` in 12). Lesson 1 is the bug class nobody had
named — aliasing — which is the one thing genuinely new.
**Best find:** `Object.freeze` has **two** failure modes in the same file,
because the judge runs CommonJS. At the top level (sloppy mode) a write to a
frozen property is **silently ignored**; inside a class body (always strict) it
**throws TypeError**. Lesson 7 teaches the contrast, and it is the sharpest
argument available for preferring a compile-time `readonly`. Both behaviours are
shipped as exercises.

**14. Utility Types** ✅ · `tools/ts_w14_utility.py` · 8 lessons, 54 exercises
`w14-why` · `w14-partial` · `w14-readonly` · `w14-pickomit` · `w14-record` ·
`w14-filter` · `w14-fntypes` · `w14-choose`.
*Capstone:* Budget Buddy #14 — a patch/update API where `EntryPatch`,
`EntrySummary` and `Totals` are all derived; stretch checks a runtime field list
against `keyof EntryPatch` with `satisfies`.
The roadmap called this "the natural first home for `design` at volume" — it
ships 2 `design` and 8 type-graded exercises, but most of the week is ordinary
stdout, because utility types change the shape of values you then print.
**Two asymmetries carry the week:** `Pick`'s key is constrained (TS2344) and
`Omit`'s is not (a typo omits nothing, silently); and `Omit` is a **type**, so a
function returning `Omit<Entry, "secret">` that does `return { ...e }` compiles
and still leaks `secret` at runtime. That leak is a shipped `fix`.

**15. Null-Safety & Error Handling** ✅ · `tools/ts_w15_nullsafety.py` ·
9 lessons, 66 exercises — the largest week in the course
`w15-absences` · `w15-optional` · `w15-chain` · `w15-nonnull` · `w15-trycatch` ·
`w15-errors` · `w15-result` · `w15-json` · `w15-validate`.
*Capstone:* Budget Buddy #15 — validate a JSON ledger, reporting
`entries[0].cents must be a number`; **8 test cases**, five of them failure
paths. Stretch collects every problem instead of stopping at the first.
The merge worked: lessons 1-7 deepen what weeks 6-11 already used, and lessons
8-9 are the genuinely new ground. `JSON.parse` returning `any` cannot be taught
with a `diagnose` — the whole point is that there is **no error** — so lesson 8
uses `_retype`, the kind that exists for exactly this, and lesson 9 earns the
type back with a real guard. That pairing is the week's payload.

**16. Modules, tsconfig & Declaration Files** ✅ · `tools/ts_w16_modules.py` ·
8 lessons, 57 exercises
`w16-module` · `w16-export` · `w16-default` · `w16-import` · `w16-shape` ·
`w16-tsconfig` · `w16-indexed` · `w16-declare`.
*Capstone:* Budget Buddy #16 — the program becomes a **package**: five sections in
dependency order, one export list, a host-supplied currency through
`declare global`, and a `satisfies`-checked strictness preset. Stretch makes the
currency a lookup with a minor-unit table (JPY prints no decimals).
Kinds: 32 drill, 14 diagnose, 7 fix, 1 predict, 1 design.

**The structural risk was real and it was settled with evidence, not a
compromise.** Every candidate was run against the real checker and the real
runner before a line was authored, and the results decided the week:

| | type-checks | runs |
|---|---|---|
| `export const` / `function` / `default` / `{ a, b }` / `type` | ✅ | ✅ |
| `export {}`, the module marker | ✅ | ✅ |
| `import * as` / `{ named }` / `{ x as y }` / default, from `"fs"` | ✅ | ✅ |
| `declare global { var X }` + `globalThis.X = …` | ✅ | ✅ |
| `interface` declaration merging | ✅ | ✅ |
| `import` from `"./money.js"` | ❌ TS2307 | ❌ ERR_MODULE_NOT_FOUND |
| `namespace N { … }` | ✅ | ❌ strip-only mode |
| `declare module "leftpad"` | ❌ TS2664 | — |

So **modules are not simulated with namespaces**. A file with a top-level
`export` genuinely *is* a module, and every export exercise is executed code; the
four import forms are taught against `"fs"`, the one module that resolves;
`namespace` gets exactly one type-graded exercise, and its unrunnability *is* the
lesson (decision 5, the same argument week 12 made against `enum`); and a
multi-file project is drawn with `// ---- money.ts ----` section comments, which
lesson 1 names as the device it is. The one impossible thing — importing a second
file — ships as a `diagnose` whose error is the genuine TS2307 and whose fix is
what a single-file project really does.

**Best find, and lesson 5's payload:** a circular import's crash reproduces
*exactly* in one file with no imports at all. A function that reads a `const`
declared below it type-checks clean (the body is deferred) and then dies with
`ReferenceError: Cannot access 'RATE' before initialization` — the same temporal
dead zone, from the same cause. Its compile-time twin is shipped beside it, where
the initialiser reads the `const` directly and TS2448 catches it; the contrast is
the teaching.

**Lesson 7 finally names `noUncheckedIndexedAccess`**, which the course has worn
since week 6 — the only place where the *configuration* is visible in every
exercise the learner has already done. Note the code: an element access has no
name to quote, so it is **TS2532**, not the TS18048 you would guess.

**Two lint holes were found while authoring and closed:** `new Map<string,
number>()` does not contain the substring `new Map(`, so the week-19 gate missed a
`Map` in week 16's capstone (now a `Record`, and `new Map<`/`new Set<` are gated
too); and `namespace `, `globalThis` and `import type ` were ungated by anything
and are now listed at 16.

### Month 5 — Async & Data Structures (weeks 17-20) — ✅ **done**

**17. Async & Promises** ✅ · `tools/ts_w17_async.py` · 9 lessons, 71 exercises —
the largest week in the course
`w17-why` · `w17-promise` · `w17-await` · `w17-order` · `w17-errors` ·
`w17-seqpar` · `w17-combinators` · `w17-typing` · `w17-patterns`.
*Capstone:* Budget Buddy #17 — a paged loader. Every page is requested at once,
the delays are deliberately reversed so the last page finishes first, and
`Promise.allSettled` reports each outcome **in page order**. Stretch gives each
page a 20 ms deadline through a per-page `Promise.race`.
Kinds: 49 drill, 9 fix, 8 diagnose, 3 predict.

**The determinism rule is in the file's header, as planned**, and it is five
clauses rather than one: order comes from the program (await in a fixed order, or
collect and print by index); nothing prints elapsed time; a race must have an
unambiguous winner (a microtask against a timer, or delays *far* apart — never two
equal delays, which is insertion order wearing a disguise); failures are driven by
a **counter**, never by timing, so a retry transcript is identical everywhere; and
delays stay in the 1-60 ms range. Every program was run four times and its stdout
compared across runs before it shipped.

Two exercises deliberately ship a program whose output is **stable but wrong** —
`w17-order` fix1 prints in completion order, `w17-seqpar` fix1 prints before the
work finishes — because a `fix` needs a starter that fails the same way every time.

**What the environment actually allows, all verified:** top-level await (with or
without an import), `Promise.withResolvers`, `Awaited<T>`, and
`Promise.all`/`allSettled`/`race`/`any`. There is no `process` and no real I/O,
which is right: a `delay()` over `setTimeout` is a truer stand-in for a slow call
than anything the judge could wait on.

**Two runtime facts the week is built on.** An unhandled rejection **kills the
process** (Node's default), so a floating promise is a crash rather than a lint
finding — which makes it a far better lesson, and it ships as two `fix`
exercises. And `return p` inside a `try` is not protected by its `catch`, because
the promise leaves the block before it settles; the starter for that one prints
nothing and exits non-zero.

**One sharp edge, found by the verifier and recorded in the file header:** Node
decides a file is an ES module by scanning for module syntax, and that scan does
**not** see an `await` that appears only inside a template expression —
`` console.log(`total ${await total(3)}`) `` as a file's sole await is parsed as
CommonJS and reports `SyntaxError: Missing } in template expression`, which says
nothing about the real problem. The two exercises that interpolate an awaited value
carry an explicit `export {};`, week 16's marker doing exactly the job week 16
said it does.

**18. Stacks & Queues** ✅ · `tools/ts_w18_stacks.py` · 8 lessons, 57 exercises
`w18-stack` · `w18-class` · `w18-brackets` · `w18-undo` · `w18-queue` ·
`w18-fastqueue` · `w18-deque` · `w18-monotonic`.
*Capstone:* Budget Buddy #18 — undo/redo over ledger commands, where each history
entry carries what reversing it needs. Stretch caps the history at three, dropping
the oldest from the other end.
Kinds: 41 drill, 8 fix, 5 diagnose, 1 predict.

**It deepens rather than introduces:** week 6 already taught `.push`, `.pop`,
`.shift` and `.unshift`, so the text is written as "you have had the operations for
twelve weeks; here is what they are FOR, and what they cost".

**The O(n) `shift` trap is taught without a clock**, which is the week's one real
find. Timing is meaningless on a four-element array and a timeout on a large one,
so lesson 5 has the learner **write the loop `shift()` hides** and count the
element moves: draining four items costs `3+2+1+0 = 6`, printed as a number and
identical everywhere. Lesson 6 replaces it with a head index and the same program
prints `moves 0`. The same technique carries the undo-history cap and, later,
week 19's quadratic de-duplication.

**One constraint shaped the whole week:** `Map` and `Set` are gated at 19, so
every lookup here is an array scan or a `Record`. That is the ladder working —
week 19 arrives as the answer to a cost already paid.

**And one trap re-found:** `constructor(private readonly limit: number) {}` is a
parameter property and dies at run time in strip-only mode (decision 5). Lesson
7's `History` class had to be rewritten the long way. Any class in a *runnable*
exercise, in any remaining week, has the same constraint.

**19. Maps & Sets** ✅ · `tools/ts_w19_maps.py` · 8 lessons, 58 exercises
`w19-why` · `w19-map` · `w19-freq` · `w19-set` · `w19-order` · `w19-identity` ·
`w19-weak` · `w19-groupby`.
*Capstone:* Budget Buddy #19 — the index: a `Map` keyed by tag plus a `Set` of
descriptions, so a duplicate is rejected in O(1) and the per-tag report is never
a filter-per-tag. Stretch compares two months with set algebra.
Kinds: 45 drill, 6 fix, 3 diagnose, 2 predict.

**Four verified facts carry the week**, each easy to get subtly wrong and each
demonstrated rather than asserted:

1. An object **reorders integer-like keys** — `Object.keys` on `b, 10, 2, a` gives
   `2,10,b,a`, where a Map gives `b,10,2,a`. The single most convincing argument
   for `Map`, and invisible until you see the output.
2. `"toString" in {}` is **true** (prototype), while `new Map().has("toString")` is
   false — so `in` is an unsafe membership test, and `Object.hasOwn` is the fix.
   Shipped as a `fix` where a validator lets `constructor` through.
3. `map.get(k)` is `V | undefined` always, so every read takes a `??` — the same
   discipline as an index access, and **TS2532** for forgetting.
4. Two structurally identical objects are **two different keys** (SameValueZero),
   which lesson 6 pairs with the canonical-key-function workaround every grid
   problem uses.

`WeakMap`'s two restrictions ship as diagnoses because the compiler's messages are
instructive: no `.size` (**TS2339**) and no primitive keys (**TS2344**, `WeakKey`).

**Two exercises had to change kind**, and the reason is worth recording: a `fix`
needs a starter that *fails*, and "slow" and "leaky" are not failures. The
quadratic de-duplication became a counted one (week 18's technique, `comparisons
0` in the answer); the WeakMap leak became a **drill about the choice** — weak for
metadata nobody iterates, strong for what the report must walk — because a lifetime
bug is by construction unobservable inside one short program.

**20. Linked Lists & Trees** ✅ · `tools/ts_w20_nodes.py` · 8 lessons, 61
exercises — **closes the Budget Buddy arc**
`w20-node` · `w20-list` · `w20-listops` · `w20-doubly` · `w20-tree` ·
`w20-traverse` · `w20-ntree` · `w20-iterators`.
*Capstone:* Budget Buddy #20 — the category tree. Indented input is parsed into a
tree **with a stack of open ancestors** (week 18 building week 20's data),
totals roll up post-order, and the report is driven by a generator that yields
`[Cat, depth]` so the printing code never recurses. Stretch adds a path query that
builds the path on the way back out and counts the nodes visited.
Kinds: 46 drill, 8 fix, 3 diagnose, 1 predict, 1 design.

**One sequencing decision, taken here rather than deferred.** Week 25 owns
"Recursion & Backtracking" and no earlier week teaches recursion — but a tree is a
recursive data structure. Three options: teach trees without recursion (contorted),
move week 25 forward (breaks the month), or **introduce recursion here, on the data
structure where it is least abstract, and let week 25 deepen it**. The third, which
is the same move weeks 13, 15 and 18 made. So lesson 5 introduces a recursive
function whose base case *is* the `| null` from the type, and **week 25 must be
written as "you have been recursing over trees since week 20; here is the whole
story"** — the call stack, the depth limit, recursion→iteration as a technique, and
backtracking (which lesson 7's path search already performs without naming).

**The best teaching in the week is only possible because week 18 came first:**
lesson 6 gives the same traversal twice, and the loop is identical —
`stack.pop()` is depth-first, a head-index dequeue is breadth-first. *DFS and BFS
are one algorithm with a different container*, which is a fact most people learn
years later than they should, and week 27 is that fact again plus a visited set.

**The `strictNullChecks` risk the roadmap flagged was real and lands in exactly one
place:** a list-walking variable must be annotated, because `let cur = head`
infers `N` and then `cur = cur.next` will not assign. Same for the `next` binding
inside `reverse`. Both ship as exercises rather than footnotes, and node shapes are
kept to two fields.

**Two `fix` starters turned out to fail at COMPILE time, and both got better
prompts for it.** The walk that advances `head` itself produces
`TS2339: Property 'next' does not exist on type 'never'` — the compiler, having
proved `head` is null after the first loop, types the second cursor as `never`,
which is a narrowing error pointing straight at a logic bug. And `yield walk(kid)`
instead of `yield*` cannot be annotated at all: the nesting grows one level per
depth.

`ts_iterators` is no longer homeless — lesson 8 covers the iterable protocol,
generator functions, generator *methods* and `yield*`, all of which run untouched
because generators are runtime syntax rather than type syntax.

### Month 6 — Algorithmic Thinking (weeks 21-24) — 🚧 **21 done**

**21. Big-O & Complexity** ✅ · `tools/ts_w21_bigo.py` · 7 lessons, 49 exercises
`w21-why` · `w21-count` · `w21-classes` · `w21-rules` · `w21-space` ·
`w21-cases` · `w21-read`.
*Capstone:* **interview rep #21** — the complexity report. Four instrumented
algorithms run at n and 2n; the ratio of the operation counts names each one's
growth class. Stretch adds a third data point and flags an algorithm whose two
ratios disagree as `unstable`.
Kinds: 40 drill, 7 fix — and **no `predict` or `diagnose`, which is deliberate
and is the one place the "use the reading kinds" rule does not apply**: complexity
produces no compiler errors to read and no inferences to name. The reading in this
week is the 28 warmup questions, the 16-question review and the counting tables
themselves, which is what those fields are for.

**The "almost nothing to judge" risk was answered by option two, and by the time
it was authored it was no longer a guess.** Weeks 18 and 19 had already proved the
technique — week 18 counts the element moves `shift()` hides (6 for four items),
week 19 counts the comparisons `includes` performs — so **every exercise in this
week instruments an algorithm and prints a count.** No fifth exercise kind was
needed.

That turned out to be the better lesson rather than a workaround. "O(n²)" is a
label; `n=4 ops=6 / n=8 ops=28 / n=16 ops=120` is the thing the label names, and a
learner who has watched a count quadruple owns the idea in a way that reciting
classes does not produce. The sizes are chosen so the arithmetic is checkable by
hand: linear gives 4/8/16, quadratic 6/28/120, binary search 4/5/6/…/11, and
`fib(n)` calls 15/177/1973.

**The capstone is the skill itself** — run at n and 2n, take the ratio, name the
class — and it classifies with **bands** rather than exact ratios, because at these
sizes the lower-order term is still visible: `pairs` at 16→32 gives 4.13, not 4.00.
The code says so, which is the honest version of a detail most treatments hide.

**Week 17's rule extends here unchanged: nothing measures elapsed time.** A
millisecond reading is noise at small n and a judge timeout at large n; a count is
an exact integer. Every "how expensive?" question in the week is answered in
operations.

**And the roadmap's "do not pad it with unrelated coding" was taken literally:**
the week introduces no new algorithms at all. Everything it measures is code from
an earlier week — week 18's `shift` and string concatenation, week 19's
`includes` scan and Map lookup, week 20's tree recursion, depth and `RangeError`.
That is also why it can afford to be this dense, and why it is the shortest week of
the back half at seven hours.

**22. Searching & Two Pointers** ⬜ · **23. Sliding Window & Prefix Sums** ⬜ ·
**24. Sorting** ⬜
Standard, low-risk, stdout-gradable. The Problem Library and
`tools/algorithms_defs.py` already hold the patterns and can seed both the
lesson text and the capstone problems.

*Two things these three inherit from week 21, which is now the month's foundation:*
binary search is already built and counted there (`w21-classes`, 11 steps at
n=1024), so week 22 should **deepen** it rather than introduce it; and each of these
weeks should report an operation count beside its answer wherever a technique's
whole point is that it is cheaper than the obvious version — which is true of all
three. A sliding window that does not show the count it saved over the nested loop
has not made its argument.

### Month 7 — DSA Interview Core (weeks 25-28)

**25. Recursion & Backtracking** ⬜ (merged from two skeleton weeks)
Base case and recursive case · the call stack · recursion → iteration ·
subsets · permutations · N-Queens · pruning.
*Note, and it changed when week 20 landed:* this week no longer **introduces**
recursion. Week 20 does, on trees, because a tree's type refers to itself and
teaching it any other way was contorted (see that week's entry). So week 25
**deepens** it, exactly as weeks 13, 15 and 18 deepen their subjects, and its file
should open with "you have been recursing over trees since week 20; here is the
whole story": the call stack and what a stack frame holds, recursion depth and the
`RangeError` (week 20 ships one as a `fix`), memoisation as a lead-in to week 26,
recursion → iteration as a deliberate technique (week 20 has both forms of every
traversal to point at), and then backtracking — which week 20's `pathTo` already
performs, returning `null` to mean "not in this subtree" so the caller tries the
next branch. Naming a pattern the learner has already used is a much better
opening than a factorial.

**26. Dynamic Programming** ⬜ · **27. Graphs: BFS & DFS** ⬜ ·
**28. Heaps & Intervals** ⬜
Standard interview ground. Heaps need a generic priority queue class — another
dependency on week 11.

### Month 8 — Advanced Types & Interview Polish (weeks 29-32)

**29. Conditional & Mapped Types** ⬜ · reuse `ts_mapped_types`,
`ts_conditional_types`
`T extends U ? X : Y` · `infer` · distributive conditionals · mapped types ·
key remapping · modifiers (`+`/`-`, `readonly`, `?`) · rebuilding `Partial`,
`Pick` and `Omit` by hand.

**30. Inference & Template Literal Types** ⬜ · reuse
`ts_template_literal_types`, `ts_keyof_indexed`
`infer` in depth · template literal types · `Uppercase`/`Capitalize` · parsing
a string at the type level · typed object paths.

**31. Type-Level Challenges** ⬜ · reuse `ts_type_level`
Recursive types · tuple manipulation · depth limits and why they exist ·
type-challenges-style puzzles.

**Weeks 29-31 are the lowest-risk content in the whole back half** — they are
graded entirely by `judge_mode: "types"`, which is proven and needs no runtime
determinism, no stdout, and no test cases. If momentum is ever needed, these
are the weeks to author.

**32. Mock Interview Week** ⬜
*Open question:* the app has no timer, so "under time" cannot be enforced.
Either make this a `brief` (unjudged) capstone with a self-scored rubric — the
`_cap_brief` helper already exists and is currently unused by the course — or
lean on the Mastery track's judged final, which already does timed assessment.

---

## Suggested batching

Each batch ends green and committable. Batch A ships no content and should
still go first.

| Batch | Weeks | Why this grouping |
|---|---|---|
| **A** ✅ | — | Generator split, practice wired, capstone arc decided, gaps sequenced |
| **B** ✅ | 11-12 | Classes unblock 18, 20, 28; structural typing completes month 3 |
| **C** ✅ | 13-16 | Types, then the project-shaped week: modules, tsconfig, .d.ts |
| **D** ✅ | 17-20 | Async + data structures; the Budget Buddy arc is closed |
| **E** 🚧 | 21 ✅, **22-24** ← next | Algorithmic thinking; 21's format is settled — count operations |
| **F** | 25-28 | DSA core |
| **G** | 29-32 | Type-level; lowest risk, highest polish |

**Batches C and D are done, and with them every risk the back half was waiting
on**: the one-file module problem (settled with evidence — week 16), async
determinism (settled with a written rule — week 17), and the recursive-node
fiddliness (settled by annotating the walker and keeping nodes to two fields —
week 20). The Budget Buddy arc ran its full twenty weeks and ended on the category
tree, as decision 2 planned.

**Four things the remaining weeks inherit, all learned the hard way:**

* **A `fix` needs a starter that FAILS.** "Slow", "leaky" and "badly shaped" are
  not failures. Where the bug is a cost, *count the operations* (weeks 18, 19);
  where it is a lifetime, make it a drill about the choice instead (week 19).
* **Nothing may print elapsed time**, and a race needs an unambiguous winner
  (week 17's rule, which now applies to week 21's complexity material too — that
  week should count operations for exactly the same reason).
* **Parameter properties never run.** Any class in a runnable exercise declares its
  fields the long way (weeks 18, 20).
* **Recursion is now introduced in week 20**, on trees. Week 25 deepens it — see
  that week's entry.

G remains independent of everything.

---

## Constraints every week must satisfy

* **Nothing before its week.** `_SCOPE_RULES` in the generator fails the build
  if a program uses a construct a later week teaches. The table was extended
  with rules for classes, `satisfies`, utility types, modules, async and
  Map/Set — **each new week must add its own rules as it lands.** Note the rules
  deliberately *omit* `readonly`, `as const`, `new`, `Record<`, `try`/`catch`/
  `throw`: weeks 8-10 already use all of them, and gating them later would be a
  false claim about when the course first shows them.
  Weeks 11-15 added `implements `, `abstract `, `super(`, `super.`, `enum `,
  `ReadonlyArray<`, `Object.freeze(`, `Object.isFrozen(`, the six remaining
  utility types (`Required<`, `Readonly<`, `Exclude<`, `Extract<`, `ReturnType<`,
  `Parameters<`), `JSON.parse(`, `JSON.stringify(` and `??=` — plus
  `NonNullable<` at 15 and `Awaited<` at 17, gated ahead of their weeks.
  All were verified clear across every authored program first.
  Two tokens were deliberately **not** added, and the reasons are recorded in
  the table itself: `extends ` (week 10 uses it 79 times for generic
  constraints, so a rule would be a false claim) and `#` (a bare `#` would match
  any stray character in a string, and `class ` already gates every private
  name, since `#x` is only legal inside a class body).
* **Erasable syntax only, unless the exercise is type-graded.** See decision 5.
  Parameter properties, `enum` and `namespace` cannot run; anything teaching
  them needs `judge_mode: "types"`.
* **Quote only errors the compiler really emits.** Every `diagnose` prompt is
  re-derived from its starter by the verifier. Batch B and C shipped four wrong
  on the first try, and the verifier caught all four. The pattern is that the
  code depends on the **syntactic form**, not just the rule:

  | you would guess | it actually is | when |
  |---|---|---|
  | TS2353 | **TS2561** | an excess property whose name is *close* to a real one |
  | TS18048 | **TS2532** | possibly-undefined on an **element access** (`xs[0]`), which has no name to quote |
  | TS2741 | **TS2345** | a missing required member in a **function argument** rather than a variable annotation |
  | — | **TS2783** | a spread that would overwrite an earlier key (`{ x: 1, ...o }`) |

  Check every candidate against `tools/ts_typecheck.mjs` before writing the prose
  around it. A small driver for this is three lines of Python and worth keeping.
* **Two helper constraints that are easy to trip over.**
  `_predict` bans the token `typeof` **anywhere in the program** (otherwise the
  answer is `typeof x`, which is in the revealed harness) — so it cannot be used
  in a lesson whose code needs `ReturnType<typeof f>`; reach for `_types` there.
  And `_predict` code must not let control-flow analysis narrow the target: a
  literal `const row: Row | null = null` narrows to `null`, and the chain below it
  then errors on `never`. Bind through a function instead.
* **The strictness ladder.** Everything from week 6 compiles under
  `strict+indexed` (`noUncheckedIndexedAccess`). Array and map access needs a
  guard, a `??` or an earned `!` — budget for it, it is a steady tax.
* **Expected output is computed, not typed.** Same trust model as the rest of
  the app.
* **Practice is scoped and judged like everything else.** It is optional to
  *complete*, never optional to be correct: it goes through the scope lint, the
  strictness ladder and both verifiers.
* **Both verifiers must pass**: `verify_ts_course.py --starters` and
  `cargo test --test verify_ts_course`.

### Adding week N

1. Write `tools/ts_wNN_topic.py` — it appends one `_week(...)` to `_WEEKS` and
   may use any helper or shared prefix from the parent.
2. Add it to `_WEEK_FILES` **in week order**, and delete the matching `_skel`
   line from the skeleton list.
3. Add that week's new syntax to `_SCOPE_RULES` — but check first that no
   earlier week already uses the token, or the rule is a false claim (this is
   how `readonly`, `as const`, `new`, `Record<` and `try`/`throw` were caught).
4. Optionally add `tools/ts_pNN_practice.py` and list it in `_PRACTICE_FILES`.
5. `python tools/gen_seed.py && python tools/verify_ts_course.py --only=wNN- --starters`

### Verification will get slow

897 exercises take ~16 minutes (Python) and ~7 minutes (Rust). A finished
course is roughly 1,900 exercises — call it **35 minutes and ~15 minutes**.
Author with `--only=wNN-` (seconds — a single week is 30-45s), and run the full
pair once per batch. If it becomes a real drag, the Python verifier's
`--types-only` flag skips execution and catches most authoring errors.

**Prove a prose-only edit is safe rather than re-running everything.** Hash a
projection of every judged program, starter, harness, test case, prompt and
strictness preset out of the seed before and after; if it is unchanged, the
verification you already ran still holds. Batch B used this after two late
lesson-text corrections.

---

## What "done" looks like

32 weeks · ~1,900 judged exercises · ~250 lessons · a Budget Buddy arc that
ends at week 20 with a real typed application · eight months of material that
never once requires syntax it hasn't taught.
