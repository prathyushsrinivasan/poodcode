# TypeScript Roadmap — Weeks 16-32

The plan for finishing **TypeScript: Zero to Interview**, the 8-month course in
`tools/typescript_course.py`. Weeks 1-15 ship; weeks 16-32 are one-line
skeletons waiting to be authored.

Unlike [`JAVA_ROADMAP.md`](JAVA_ROADMAP.md), which starts after the basics, this
course starts at *zero* — week 1 is someone's first line of code. That decision
is what makes the back half hard: everything in weeks 16-32 must still obey the
rule that nothing may require syntax a later week teaches.

**Status legend** — ✅ built and shipping · 🚧 partially built · ⬜ planned.

---

## Where it stands

**Built:** weeks 1-15 — **119 lessons, 897 judged exercises** (882 in lessons and
capstones, 15 in week 1's practice families), fifteen Budget Buddy capstones, and
a complete glossary/cheat-sheet/self-check/review set per week.

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
`_M4` now sits with `_M1`-`_M3` above the loop, and **`_M5` must be moved up the
same way before week 17 is authored.**

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

### Month 4 — Robust, Real-World Programs (weeks 13-16) — 🚧 **13-15 done, 16 outstanding**

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

**16. Modules, tsconfig & Declaration Files** ⬜ · reuse `ts_modules`,
`ts_tsconfig`, `ts_declaration_files`
`import`/`export`, named vs default · barrel files · circular imports ·
`strict` and what each flag buys · `noUncheckedIndexedAccess` (the course has
been running under it since week 6 — name it at last) · `.d.ts` · `declare` ·
ambient types · typing an untyped dependency.
*Risk:* **highest structural risk in the course.** The judge compiles **one
file**; there is no module resolution and no second file. Modules must be
taught with single-file-compatible examples (namespaces of a sort, or
`export` used but never imported across files) and the lesson must be honest
that the exercises simulate a multi-file project. Decide this approach before
authoring, or the week will be rewritten.

### Month 5 — Async & Data Structures (weeks 17-20)

**17. Async & Promises** ⬜ · reuse `ts_async`, `ts_async_patterns`
Promises · `async`/`await` · error handling in async code · `Promise.all` /
`allSettled` / `race` · sequential vs concurrent · typing async functions.
*Risk:* **determinism.** This is the TypeScript analogue of the Java course's
Part 10 problem, and the same discipline applies: output must be deterministic
*by construction*. Await in a fixed order, or collect results and print in
index order — never let timing decide output. Record the rule in the week
file's header, as `java_m30_sync.py` does.

**18. Stacks & Queues** ⬜ · reuse `ts_ds_generics`
Array as stack · queue and the O(n) `shift` trap · a generic `Stack<T>` and
`Queue<T>` class (needs week 11) · balanced brackets · monotonic stack.
*Capstone:* Budget Buddy #18 — an undo/redo stack.

**19. Maps & Sets** ⬜ · reuse `ts_maps_sets`
`Map` vs an object as a lookup · `Set` and de-duplication · iteration order ·
keying by object identity · `WeakMap` briefly · frequency counting.

**20. Linked Lists & Trees** ⬜ · reuse `ts_ds_generics`, `ts_iterators`
Node types and the recursive type that describes them · singly and doubly
linked lists · binary trees · traversals · a tree of expense categories ·
iterators and generators (`ts_iterators` is otherwise homeless).
*Capstone:* Budget Buddy #20 — the category tree. **Closes the arc.**
*Risk:* medium-high. Recursive generic node types under
`noUncheckedIndexedAccess` and `strictNullChecks` get fiddly fast; keep node
shapes small and lean on `design`.

### Month 6 — Algorithmic Thinking (weeks 21-24)

**21. Big-O & Complexity** ⬜
*Risk:* **this week has almost nothing to judge.** Complexity is a reasoning
skill, and the course's grading model is "run it and compare stdout". Options,
in preference order: lean heavily on `warmup`/`quiz`/`review` (all already
supported, and this is what they are for); write exercises that *measure*
(count operations into a counter and print it, so the shape of the growth is
the output); and consider a fifth kind, `predict-the-cost`, if quizzes prove
too thin. Do not pad it with unrelated coding.

**22. Searching & Two Pointers** ⬜ · **23. Sliding Window & Prefix Sums** ⬜ ·
**24. Sorting** ⬜
Standard, low-risk, stdout-gradable. The Problem Library and
`tools/algorithms_defs.py` already hold the patterns and can seed both the
lesson text and the capstone problems.

### Month 7 — DSA Interview Core (weeks 25-28)

**25. Recursion & Backtracking** ⬜ (merged from two skeleton weeks)
Base case and recursive case · the call stack · recursion → iteration ·
subsets · permutations · N-Queens · pruning.
*Note:* this week now carries the recursion fundamentals that used to sit in
month 5, so it must start gentler than a pure backtracking week would.

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
| **C** 🚧 | 13-15 ✅, **16 left** | Types done; 16 was split off — see below |
| **D** | 17-20 | Async + data structures; closes the Budget Buddy arc |
| **E** | 21-24 | Algorithmic thinking; 21 needs its format decided first |
| **F** | 25-28 | DSA core |
| **G** | 29-32 | Type-level; lowest risk, highest polish |

**Week 16 is now the only thing standing between the course and month 5**, and it
is deliberately left last in its batch because it is the highest-risk week in the
course — see its entry above, plus decision 5 on `namespace`. It blocks nothing:
weeks 17-20 need classes (batch B) and nothing from 16, so **D can start
immediately** and 16 can land whenever its format is settled. G remains
independent of everything.

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
