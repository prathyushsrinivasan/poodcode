# TypeScript Roadmap — Weeks 31-32

The plan for finishing **TypeScript: Zero to Interview**, the 8-month course in
`tools/typescript_course.py`. Weeks 1-30 ship; weeks 31-32 are one-line
skeletons waiting to be authored.

Unlike [`JAVA_ROADMAP.md`](JAVA_ROADMAP.md), which starts after the basics, this
course starts at *zero* — week 1 is someone's first line of code. That decision
is what makes the back half hard: everything in weeks 24-32 must still obey the
rule that nothing may require syntax a later week teaches.

**Status legend** — ✅ built and shipping · 🚧 partially built · ⬜ planned.

---

## Where it stands

**Built:** weeks 1-30 — **230 lessons, 1,626 judged exercises** (1,611 in lessons
and capstones, 15 in week 1's practice families), twenty Budget Buddy capstones —
**the arc is complete** — eight interview reps, and a full
glossary/cheat-sheet/self-check/review set per week. **Months 6 and 7 are finished.**

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

## State of play — what is proven, and what will bite you

Written for whoever picks this up next, including me. Nothing here is a plan; it
is the stuff that is only obvious after it has cost you an hour.

### Verification status, precisely

| | covers | last run |
|---|---|---|
| `python tools/verify_ts_course.py --starters` | weeks 1-23 in full; **weeks 24-30 one at a time (`--only=wNN-`), 0 failures each** | current |
| `cd src-tauri && cargo test --release --test verify_ts_course` | **weeks 1-28 (batch F's closing run), 1,557 exercises, 3 tests, all green** | weeks 29-30 not yet |

The Rust suite is the judge-level one — it puts every program through the same
judge the app uses, rather than through the fast Node path. The old gap (weeks
22-23 never judge-verified) is closed. The suite now runs **once per batch**, as
"Verification will get slow" recommends, started in the background right after a
batch's last week is committed; weeks 29-30 landed after it and are covered by the
Python verifier until batch G's closing run. Each new week was verified alone,
which is sufficient because adding a week leaves every earlier week of the seed
**byte-identical** (checked by comparing each week's JSON against the previous
commit's).

**Timing, recorded honestly:** the weeks 1-25 run took 914 s; the weeks 1-28 run took
**6,545 s**, because it shared the machine with the authoring of weeks 29-30 (the
Python verifier and `gen_seed.py` both spawn Node). Nothing failed — the judge's
timeouts are generous — but it is the memory note "run judge-heavy suites alone"
measured: alone, expect about 15 minutes.

One thing to know before running it: the test `include_str!`s `ts_course.json` at
**compile time**. A run already in progress when you regenerate the seed is
testing the old seed — stop it and start again.

Note that the Python verifier prints a `note:` listing `fix` starters that fail at
**compile** time rather than at run time. That note is informational — 32 such
starters exist across the whole course, most of them from weeks 1-10 — and it is
worth reading when you add a `fix`, because a compile-time failure teaches something
different from a runtime one. Two in week 20 were deliberately re-prompted once the
verifier revealed which kind they were.

### Nothing is half-finished

Every authored week is complete: lessons, exercises, capstone, stretch, glossary,
cheat sheet, self-check, review, milestone. Weeks 31-32 are untouched skeletons, as
they were before. There is no partially-authored week and no disabled exercise.

### Five traps that cost real time

1. **Parameter properties do not run.** `constructor(private readonly x: number) {}`
   type-checks and then dies with
   `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX` in strip-only mode. Week 11 knew this and
   grades them with `judge_mode: "types"`; weeks 18 and 20 both walked into it
   anyway. **Any class in a runnable exercise declares its fields the long way.**

2. **Node's module detection cannot see an `await` inside a template literal.**
   A file whose only top-level await is `` `${await f()}` `` is parsed as CommonJS
   and reports `SyntaxError: Missing } in template expression`, which says nothing
   about the real problem. Two week-17 exercises carry an explicit `export {};` for
   this. If a program uses top-level await *only* inside a template, add one.

3. **The scope lint matches substrings, so generic forms slip past it.**
   `new Map<string, number>()` does not contain `new Map(`, and a `Map` therefore
   reached week 16 despite the week-19 gate. Both generic spellings are now listed.
   **When you gate a constructor, gate `new X<` as well as `new X(`.**

4. **A `fix` needs a starter that FAILS — and "slow", "leaky" and "badly shaped"
   are not failures.** The verifier rejects a buggy starter that passes, which is
   correct and catches this every time. Three exercises had to be redesigned:
   * where the bug is a **cost**, count the operations and let the count be wrong
     (week 18's `shift`, week 19's `includes`, week 21 throughout);
   * where the bug is a **lifetime**, it is unobservable in a short program —
     week 19's WeakMap leak became a drill about the *choice* instead;
   * where the bug is a **wrong technique**, you must find an input that actually
     breaks it. Week 23's sliding-window-on-negatives looked broken on `[1, -2, 3]`
     and is not; `[5, -5, 1]` with a budget of 1 is a real failure. That an obvious
     input did not expose it is now part of the exercise's own prompt.

5. **Expected outputs must be computed, never typed.** Several capstone outputs
   were written by hand and were wrong — week 17's total, week 20's, week 21's
   column widths, three of week 23's. The reliable loop is: put a placeholder in the
   test, generate the seed, run the reference solution out of `ts_course.json`, and
   paste what it actually printed. The Mastery track has `_computed()` for exactly
   this; the course does not, and adding it would be a genuine improvement.
   Week 24 is the latest evidence: of 55 outputs worked out by hand, **three were
   wrong** (a middle-pivot quicksort count of 49 that is really 38, and an insertion
   count of 8 that is really 10, stated in three places). The verifier caught all
   three on the first run; `verify_ts_course.py` prints `got:` beside `expected:`,
   which is the number to paste.

### Two claims that were wrong and are now corrected

Both were caught by the verifier rather than by review, which is worth knowing about
how much the verifier is doing:

* **Week 22** claimed that comparing against `xs[read - 1]` instead of
  `xs[write - 1]` in an in-place dedupe was a bug. It is not — the two are
  equivalent, because `write <= read` means the slot at `read - 1` can only be
  overwritten when `write === read`, which is a no-op. The lesson now says that and
  argues from *what the code means* instead.
* **Week 23** claimed a difference array sized `n` rather than `n + 1` was
  observably broken. It is not — writing past the end of a JavaScript array just
  grows it. That `fix` now teaches the missing second write, which genuinely leaks
  the adjustment to the end of the array.

### One pre-existing breakage fixed along the way

`gen_seed.py` failed at the commit this work started from: `tsm-w10-vending` in
`tools/mastery_ts_more_m3.py` had a reference solution that did not type-check
(**TS7022** — the narrowed `state` fed back into `next`'s own initializer), so its
computed outputs had never been generated. Annotating the destructured tuple fixed
it. Unrelated to the TypeScript course, but nothing could be built until it was.

### Where the shared constraints now live

Two documents carry rules that apply beyond a single week, and both are worth
reading before authoring 24-32:

* **`tools/ts_w17_async.py`'s header** — the determinism rule, in five clauses. It
  governs any week that touches timing, and week 21 extended it to "nothing measures
  elapsed time, ever".
* **`tools/ts_w21_bigo.py`'s header** — why every measurement in month 6 is an
  operation count, with the sizes chosen so the arithmetic is checkable by hand.

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

### Month 6 — Algorithmic Thinking (weeks 21-24) — ✅ **done**

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

**22. Searching & Two Pointers** ✅ · `tools/ts_w22_search.py` · 7 lessons,
47 exercises
`w22-linear` · `w22-binary` · `w22-bounds` · `w22-answer` · `w22-twoends` ·
`w22-samedir` · `w22-merge`.
*Capstone:* **interview rep #22** — the search toolkit. One sorted ledger, five
query types (present / insertion point / count / range count / nearest), each built
from the two bounds and each printing the binary-search steps it cost. Stretch adds
a two-pointer pair-sum query so the sweep's step count sits beside the search's on
the same data.
Kinds: 37 drill, 7 fix, 1 predict.

**It deepens binary search rather than introducing it** — week 21 already built and
counted one — so the week spends its time on the three things that make it useful:
the two **bounds** (which is what almost every real use is), searching **on the
answer**, and the boundary that breaks it.

**The off-by-one is taught as a table with two rows** — inclusive `hi` with
`lo <= hi` and `hi = mid - 1`, or exclusive `hi` with `lo < hi` and `hi = mid` —
and "every binary search bug is a value from one row used with the other". The
`fix` ships the mixed version, whose giveaway is that **a one-element array fails**:
`search([1], 1)` returns -1. That is the cheapest test in programming and almost
nobody writes it.

**Mid-point overflow is explicitly NOT taught as a bug here.** `lo + hi` exceeding
the integer range is real in Java and C (it sat in the JDK for nine years) and
cannot happen with JavaScript doubles, so the lesson says so and explains where the
`lo + (hi - lo) / 2` idiom people copy comes from, instead of repeating advice that
does not apply.

**One authoring correction worth recording, because it is the kind of thing that
ships as a confident falsehood.** The in-place dedupe lesson originally claimed that
comparing against `xs[read - 1]` instead of `xs[write - 1]` was a *bug*. The
verifier disagreed — the buggy starter passed — and testing showed the two are
genuinely **equivalent** here, because `write <= read` means the slot at `read - 1`
can only be overwritten when `write === read`, which is a no-op. The lesson now says
that, and makes the honest argument instead: `xs[write - 1]` is correct because of
what it means, `xs[read - 1]` is correct because of a two-line argument about
indices, and the second kind of correctness stops being true when somebody edits the
loop. The `fix` was replaced with a bug that is real — a missing empty-array guard,
which reports **1** kept element out of nothing.

**And the month's counting habit continues:** five exercises and both capstones
print a step count beside the answer, because "two pointers is O(n)" is a claim and
`steps=5` next to `pairs=15` is the evidence.

**23. Sliding Window & Prefix Sums** ✅ · `tools/ts_w23_windows.py` · 7 lessons,
45 exercises
`w23-fixed` · `w23-variable` · `w23-counts` · `w23-prefix` · `w23-submap` ·
`w23-diff` · `w23-choose`.
*Capstone:* **interview rep #23** — the ledger analytics report. Four questions
about one ledger, each answered with a different technique from the week (prefix
table, fixed window, variable window, prefix+Map) and each printing the operations
it cost. Stretch adds the fifth technique, a difference array.
Kinds: 36 drill, 7 fix.

**The roadmap asked this week specifically to show its counts** — "a sliding window
that does not show the count it saved over the nested loop has not made its
argument" — so lesson 1 ships both versions of the same problem and prints both:
11 operations against 15 on a seven-element array, and the exercise that follows
extends it to n=1000, k=100, where it is **1,900 against 90,100**. That second
number is the one that makes the point.

**Lesson 7 is the week's actual payload**, and it is a table rather than an
algorithm: *"contiguous" → window; a fixed count → fixed window; "longest … such
that" → variable window; repeated range totals → prefix sums; "count the subarrays"
→ prefix + Map; many updates then one read → difference array.* All five are short
once chosen; choosing is the skill.

**The one thing that decides between a window and prefix+Map is whether the values
can be negative**, and that is stated as its own lesson-2 section, because a window
silently returns a wrong answer rather than failing.

**Three sentinels, named as one idea.** The prefix array's leading `0`, the
difference array's `n + 1`th slot, and week 20's sentinel node are the same trade —
one wasted slot in exchange for deleting a branch — and lesson 6 says so explicitly.
Three appearances in one course is worth pointing at.

**24. Sorting** ✅ · `tools/ts_w24_sorting.py` · 7 lessons, 55 exercises
`w24-simple` · `w24-merge` · `w24-quick` · `w24-counting` · `w24-builtin` ·
`w24-tool` · `w24-choose`.
*Capstone:* **interview rep #24** — the sort bench. Five hand-written sorts
(insertion, selection, merge, quick, counting) run on one input, each checked
against the built-in and each reporting its comparisons — counting sort reports
`ops` instead, because it never compares. The tests are chosen so each sort takes a
turn at looking good and bad: sorted input makes insertion cheapest and last-element
quicksort as bad as selection; `3 1000 2` makes counting sort walk 1,001 buckets.
Stretch benches **stability** instead of cost.
Kinds: 36 drill, 13 fix, 2 diagnose, 1 predict, 1 function exercise (`_fn` —
"write insertion sort", graded on the returned array).

**Everything the roadmap said it inherits, it used.** Merge sort is three new lines
around week 22's merge, and the file header lists what came from where (week 6's
comparator, week 19's `||` tie-break, week 20's recursion, week 21's counting,
week 22's merge and partition, week 23's prefix sums). The week opens on how the
sorts work, not on whether to sort.

**The counts carry the argument, as the month requires**, and every one is
checkable by hand: selection sort does 28 comparisons on *any* eight elements
("its cost ignores its input"), insertion sort 7 sorted and 28 reversed ("its cost
depends on it" — week 21's best/worst case as two numbers from one program), merge
sort 12/32/80 at n = 8/16/32 against n log n = 24/64/160, and last-element quicksort
**120 on sorted input against 64 on mixed** — selection sort's number, on the input
you would think was easiest. A middle pivot brings it to 38.

**Two runtime facts found while probing, and both became exercises:**

* A comparator that never returns a negative — `(a, b) => (a > b ? 1 : 0)` —
  **type-checks and does not sort**: `[3, 1, 2]` comes back `3,1,2`, because the
  engine only moves an element when told it belongs earlier. A `fix` with no error
  message and no warning, which is exactly what makes it worth a lesson.
* A boolean comparator is **TS2345**, and at run time it *also* leaves the array
  unsorted — so the compile error reads as a rescue rather than pedantry. Shipped as
  a `diagnose`, beside **TS2339** for `.sort` on a `readonly number[]` (the type
  system's version of week 6's "sort mutates").

**Lesson 4 closes the loop on the lower bound.** `⌈log₂ n!⌉` is computed as a sum of
`Math.log2(i)` (5 / 16 / 45 for n = 4 / 8 / 16), merge sort's worst eight elements
cost 17 against a floor of 16, and the middle-pivot quicksort's 38 on sixteen sorted
elements — *under* the floor of 45 — gets a sentence explaining why that is no
contradiction: the bound is about the worst input. Counting sort then steps around
it, and its **stable** form is week 23's prefix sum doing a new job.

**Two further `fix` exercises are silent data loss rather than crashes**: counting
sort on negative values (`counts[-2]` sets a *property*, which the index walk never
visits, so `-2` simply vanishes) and the emit loop stopping at `v < max`.

**Quicksort's instability is exhibited, not asserted** — on `ann 2, bo 1, cy 2,
dee 1` it puts `dee` before `bo` — and the stretch's hints make the honest point
that `ties kept` on one input proves nothing: stability is a guarantee, and only its
absence can be shown by example. Its second test is an input where quicksort happens
to keep its ties.

**One new scope rule**: `.toSorted(` gated at 24. Week 13's lesson prose mentions it
in passing; no program before this week calls it.

### Month 7 — DSA Interview Core (weeks 25-28) — ✅ **done**

**25. Recursion & Backtracking** ✅ · `tools/ts_w25_recursion.py` · 7 lessons,
46 exercises
`w25-stack` · `w25-shape` · `w25-loops` · `w25-subsets` · `w25-perms` ·
`w25-prune` · `w25-recognise`.
*Capstone:* **interview rep #25** — every combination summing to a target, each
candidate used once, duplicates in the input but never in the output, with the
calls counted. Sorting does two jobs (legal `break` pruning, and adjacent
duplicates to skip); the `4 4 4 4 → 8` test is one answer only because of the skip.
Stretch: N-Queens, printing the first board and the solution/visit counts.
Kinds: 31 drill, 9 fix, 2 diagnose, 1 design, 1 retype.

**It deepens, as planned**: the file opens with "you have been recursing since
week 20", and lesson 7 opens on week 20's `pathTo` — `return null` *is* the
backtrack — before rewriting it with an explicit `path` and `pop`.

**Three TypeScript facts carry lessons 1-2, all verified:** a recursive function
with no return annotation is **TS7023** (its type depends on itself, so inference
refuses), the forgotten `return` on the recursive branch is **TS2366** (and would
silently print `undefined` without the annotation), and a **recursive type**
(`type Nested = number | readonly Nested[]`) ships as a `_design` whose harness uses
`// @ts-expect-error` to prove the learner's type *rejects* `[1, "two"]` — an `any`
leaves the directive unused, which is itself an error. That is a new trick for
type-graded harnesses and worth reusing in weeks 29-31.

**The depth limit is taught without printing it.** A 100,000-node list recursed
one node per call is a `RangeError` on the judge's Node (verified), and the `fix` is
a loop — but no exercise prints "the maximum depth", because it varies with frame
size and engine flags. Week 17's determinism rule, applied to the stack.

**Month 6's counting idiom carries over as "calls made":** 8 leaves and 15 calls for
the subsets of three; 24 permutations and 65 calls for four; pruning on `1…8` →
target 8 visits 25 nodes against 223 unpruned; and lesson 7's lead-in to week 26 —
stair-climbing for 20 stairs is **21,891** calls naively and **39** memoised.

**Two `fix` exercises are aliasing and state bugs rather than crashes**, which is
what backtracking actually goes wrong with: `out.push(path)` without a copy prints
`[]` for every subset, and resetting `path` but not `used[i]` produces exactly one
permutation. A third is a memo written under `n - 1`, which is fast *and* wrong
(`ways=384` for 10 stairs).

**One trap found while authoring and recorded in the stretch's hints:** `let first:
T | null = null` assigned inside a nested function is still narrowed to `null`
afterwards — TypeScript does not see assignments made in closures — so the stretch
keeps its first board in an array instead.

Its three hand-counted call totals were wrong on the first run (25 not 24, 223 not
256, 17 not 12) — trap 5 again; all now come from the reference.

**26. Dynamic Programming** ✅ · `tools/ts_w26_dp.py` · 7 lessons, 41 exercises
`w26-memo` · `w26-table` · `w26-state` · `w26-grid` · `w26-strings` ·
`w26-knapsack` · `w26-choose`.
*Capstone:* **interview rep #26** — the coin report: fewest coins *and which ones*
(reconstructed from a recorded choice per amount), greedy's answer beside it, and
the number of combinations. One test is an input where greedy reaches the amount
badly (`1 3 4 → 6`: 4+1+1 against 3+3); another is one where greedy **cannot reach
it at all** while DP can (`5 3 → 9`). Stretch: edit distance with the edits listed.
Kinds: 30 drill, 7 fix, 1 diagnose, 1 predict.

**It starts exactly where week 25 stopped** — 21,891 calls against 39 — and lesson
1 generalises the Map: the key is the *whole state*, keyed with week 19's
`` `${r},${c}` `` trick. The recipe (state → transition → base → order → answer) is
lesson 3, and every later lesson is that recipe applied, as the week's summary
promises.

**Three TypeScript facts, all verified, that no generic DP course would teach:**

* `new Array(n).fill(0)` is **`any[]`** — every tutorial's DP table, and the checker
  then accepts `dp[0] = "oops"`. Shipped as a `_predict` whose answer is `any[]`;
  every table in the week is `new Array<number>(n)`.
* `if (memo.has(n)) return memo.get(n);` is **TS2322** — `has` does not narrow
  `get`. A `diagnose`, fixed with week 19's get-then-compare idiom.
* `new Array(R).fill(new Array(C).fill(0))` is one row, R times (week 13's
  aliasing). The week's grid helpers (`makeGrid`/`at`/`put`) use `Array.from`.

**Two `fix` starters passed on the first run, and both findings are now part of the
teaching:**

* **The aliased-rows table computed the right corner.** With one shared row, the
  grid-paths loop *becomes* lesson 4's one-row rolling version, so `28` came out
  right. The exercise now prints the whole table — every row comes out as the last
  row — and the prompt says why the corner survived: "a table you cannot trust away
  from its corner is not a table".
* **The off-by-one LCS comparison (`charAt(i)` for `charAt(i - 1)`) gave 3 on
  `abcde`/`ace`.** Two errors cancel: it skips the first characters, and at the last
  cell both `charAt` calls run off the end and return `""` — which equals `""`. It
  now tests `abc`/`xbc` (prints 3, answer 2), and the prompt explains the phantom
  match. Trap 4 again: finding the input that breaks a wrong technique is part of
  writing the exercise.

**Loop order as meaning, twice.** Coin *combinations* need the coin loop outside
(4 for amount 5 with 1, 2, 5); swapped, the same code counts *sequences* (9) — a
`fix` whose every line of arithmetic is right. And 0/1 knapsack in one row must walk
capacity backwards; forwards packs one item three times (9 against 3) and is exactly
right for the unbounded version, which lesson 6 also runs.

All 41 hand-written expected outputs were right on the first run — the first week
where that happened. Two `fix` prompts quoted the wrong buggy output (4 for 7, and
1 for 0) and were corrected from the starters' real output.

**27. Graphs: BFS & DFS** ✅ · `tools/ts_w27_graphs.py` · 7 lessons, 39 exercises
`w27-model` · `w27-dfs` · `w27-bfs` · `w27-grids` · `w27-order` · `w27-levels` ·
`w27-weighted`.
*Capstone:* **interview rep #27** — the maze: BFS from `S` with a stated neighbour
order (up, down, left, right — which is what makes "the" shortest path well
defined), the route drawn with `*` from parent links, and `explored` counted as
cells dequeued. Stretch: a course planner — Kahn's algorithm taking the
smallest-numbered available course first, plus the fewest semesters (the longest
path, a week-26 DP over the topological order).
Kinds: 28 drill, 7 fix, 1 predict, 1 diagnose.

**Week 20's promise, kept literally.** Lesson 2 opens on "stack → DFS, queue → BFS,
plus a visited set", and the traversal loops are week 20's with a `Set` added.
Every BFS uses week 18's head-index queue; recursive DFS appears only where depth is
small, and the grid lessons use an explicit stack for week 25's reason.

**The TypeScript fact, verified:** `Array.from({ length: n }, () => [])` infers
**`never[][]`**, so the first `push` is TS2345. Shipped as a `_predict` (answer
`never[][]`) and a `_diagnose`; every adjacency list in the week annotates the
callback, `(): number[] => []`.

**Bugs chosen because they are silent:** one-way edges in an undirected graph; a
grid neighbour computed as `id - 1`, which wraps to the previous row and merges two
islands on opposite edges; the undirected cycle rule applied to a directed graph,
which calls a diamond a cycle (fixed with three colours); multi-source BFS seeded
with one source; marking on dequeue (right distances, 6 queue entries for 5 nodes —
a counted cost bug, per trap 4); and BFS on weighted edges, which answers 5 where
the cheapest route is 3.

**The lead-in to week 28 is deliberate.** Lesson 7 fixes the weighted case with an
O(V²) array-scan Dijkstra and counts its scans (16 for four nodes), then says what
step 1 really needs: "the smallest item, repeatedly, as items arrive". Week 28's heap
is the answer to a cost the learner has just paid — the same move weeks 18 → 19 made.

Two expected outputs were wrong on the first run (7 reachable cells, not 6, and the
maze path — which goes down first under the stated order). One capstone test was
replaced because it did not do what the brief claimed of it; its output was taken
from the reference, as was every other number. Two `fix` prompts misquoted their
starters' output and were corrected from real runs.

**28. Heaps & Intervals** ✅ · `tools/ts_w28_heaps.py` · 7 lessons, 34 exercises —
**closes Month 7**
`w28-shape` · `w28-class` · `w28-uses` · `w28-merge` · `w28-rooms` · `w28-greedy` ·
`w28-review`.
*Capstone:* **interview rep #28** — the scheduler: merged busy blocks, rooms needed
(a min-heap of end times), and the most meetings one person can attend (the
earliest-end greedy), on one dataset. The back-to-back test is where the three
questions deliberately treat touching meetings differently. Stretch: the running
median with two heaps.
Kinds: 25 drill, 6 fix, 1 diagnose.

**It opens on week 27's cost**, as planned there: Dijkstra's "smallest item,
repeatedly, as items arrive" was a counted O(V) scan, and the heap is the answer —
the weeks 18 → 19 move again. Lesson 3 then runs Dijkstra with the heap and **lazy
deletion**.

**The generic class the roadmap called for** — `MinHeap<T>` with a comparator — obeys
trap 1: **no parameter properties**, every field declared the long way, and lesson 2
says why in the prose rather than leaving it to a footnote. It also needs no `!`
anywhere: comparisons go through a private `less(i, j)` that treats a missing slot as
"not less", which is the week's answer to "a generic `T` has no default to fall back
to". Max-heaps are the same class with `(a, b) => b - a`.

**Determinism was designed in, not patched.** A heap is not stable, so every exercise
that pops records breaks ties in its comparator (by name) — two correct heaps then
produce the same output. Intervals are half-open `[start, end)` throughout, and the
one place touching blocks merge (busy time) says so in the brief.

**Silent bugs as fixes:** sift-down into the larger child; top-k with a max-heap
(keeps the three *smallest*); a merge that takes the newcomer's end (a block with an
interval inside it shrinks); merging unsorted input (which prints only `8-10` for
`8-10 1-3 2-6` — both earlier intervals are swallowed into the first block); the
sweep-line tie with starts before ends (two rooms for back-to-back meetings); and
the interval greedy sorted by start.

**Greedy, proved rather than asserted.** Lesson 6 gives the exchange argument for
"earliest end first", and an exercise runs three greedy rules side by side on two
counter-examples — the way to reject a greedy rule, contrasted with week 26's coin
change where no such argument exists.

All 34 expected outputs were right first time; three `fix` prompts misquoted their
starters' output and were corrected from real runs.

### Month 8 — Advanced Types & Interview Polish (weeks 29-32) — 🚧 **29-30 done**

**29. Conditional & Mapped Types** ✅ · `tools/ts_w29_mapped.py` · 7 lessons,
35 exercises (25 type-graded)
`w29-conditional` · `w29-distribute` · `w29-infer` · `w29-mapped` · `w29-remap` ·
`w29-runtime` · `w29-library`.
*Capstone:* **Library #1 — the config module** (decision 2's typed library begins):
JSON overrides typed as `DeepPartial<Config>`, a generic `mergeDeep` that keeps a
nested override's siblings, and a result that is `DeepReadonly<Config>` to the
compiler *and* `deepFreeze`d at run time. Graded on stdout **and** type assertions.
Stretch: `DeepMutable` and `Settable` (object-valued keys remapped away).
Kinds: 28 drill (most type-graded), 2 diagnose, 2 fix, 1 design.

**Rebuilding the built-ins is graded honestly.** `Equal<Optional<E>, Partial<E>>` is
satisfied by writing `Partial<E>`, so `_types` gained a `forbid` parameter (the
judge's existing substring ban, which exempts the hidden harness) and every rebuild
bans its built-in's name. The rebuilt types get their own names — `Optional`,
`Frozen`, `Needed`, `Keep`, `Drop`, `Without`, `Only`, `Present`, `Ret`, `Args` — partly
because `MyPartial<` contains the banned substring `Partial<`. (The same trap caught
`DeepPartial<T`, which contains `Partial<T`; the verifier's `check_forbidden` refused
the build, as it should.)

**Every equality was probed against the checker before a line was written**, including
the subtle ones: the key-remapped `Drop` *is* `Equal` to `Omit` (modifiers survive the
`as` clause); `DeepReadonly` turns `number[]` into `readonly number[]`; and a
distributive conditional over `never` is `never`, which is why `IsNever` must wrap
its parameter in a tuple — shipped as the lesson's hardest exercise.

**`@ts-expect-error` proves rejections**, the device week 25 introduced. In the
capstone it sits in a function that is never called, so a write to the frozen config
is type-checked (and must be rejected, or the unused directive fails the check with
TS2578) but never executed — which matters, because in an ES module that write
would throw.

**Lesson 6 puts the types back onto running code**, graded on stdout plus
assertions, and its `fix` is week 14's `Omit` leak one level up: a `pick` typed as
returning `Keep<T, K>` that spreads the whole input prints all four keys. A type is
not a runtime filter.

Two new scope rules: `infer ` and `in keyof`, both at 29, verified absent from every
earlier program. Every expected output and every `fix` prompt was right first time.

**30. Inference & Template Literal Types** ✅ · `tools/ts_w30_template.py` ·
7 lessons, 34 exercises (22 type-graded)
`w30-template` · `w30-match` · `w30-infer` · `w30-parse` · `w30-paths` ·
`w30-literal` · `w30-library`.
*Capstone:* **Library #2 — the router** decision 2 named: handlers typed from their
pattern strings (`"/users/:id/posts/:postId"` → `{ id: string; postId: string }`),
routes stored type-erased with one cast in `add`, `add` returning `this` so
registrations chain, and segment-by-segment resolution with a 404. The harness
proves `(p) => p.name` on `/users/:id` does not compile. Stretch: a typed message
formatter whose values object must name exactly the template's `{placeholders}`.
Kinds: 27 drill (most type-graded), 2 diagnose, 2 fix, 1 predict.

**Every type in the week was probed before it was written** — including the ones
that look too clever to be true: a template of two unions multiplies (`${"a"|"b"}-${1|2}`
has four members), `infer N extends number` turns `"42"` into the literal `42`,
`Paths<Config>` is exactly `"name" | "db" | "db.host" | "db.port"`, and a `const`
type parameter keeps `["a", "b"]` as `readonly ["a", "b"]`.

**The key-type trap is a diagnose, not a footnote:** `Capitalize<K>` with
`K in keyof T` is **TS2344**, because `keyof` may include number and symbol keys;
`K & string` is the idiom every library uses. **Widening** gets one too — `let
method = "GET"` is `string`, which a `"GET" | "POST"` parameter rejects (TS2345).

**A new helper, `_typed`,** grades a runtime *drill* on stdout and on harness
assertions (week 29 did this through `_mk` directly for its capstone). Lesson 5's
typed `get(config, "db.port")` is graded both ways: it must print `5433`, its result
must be `number`, and `get(config, "db.prot")` must not compile. Its `fix` is the
case the types cannot catch — a walk that splits on `/` while the type says `.`
prints `undefined` — "types describe; code does".

Four new scope rules: `Uppercase<`, `Lowercase<`, `Capitalize<`, `Uncapitalize<`, at 30.
Every expected output and `fix` prompt was right first time; one quiz question was
caught garbled in review before generation.

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
| **E** ✅ | 21-24 | Algorithmic thinking; the month's idiom is to count operations |
| **F** ✅ | 25-28 | DSA core |
| **G** 🚧 | 29-30 ✅, **31** ← next | Type-level; lowest risk, highest polish |

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
  Weeks 16-24 added the module tokens, `async`/`await`/`Promise<`, `Map`/`Set`
  in both constructor spellings, generators, and `.toSorted(` at 24.
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
