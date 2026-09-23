# TypeScript Mastery Roadmap — the 6-Month programme

The plan for turning the **TypeScript track of the 6-Month Mastery programme**
(`/mastery`, authored in `tools/mastery_defs.py`, served from
`src-tauri/seeds/mastery.json`) from a well-sequenced *reading list* into a
programme someone could actually come out of fluent.

This is not the same thing as [`TS_ROADMAP.md`](TS_ROADMAP.md). That document
plans **TypeScript: Zero to Interview** (`/ts-course`, 32 weeks, 897 judged
exercises, seven exercise kinds). This one plans the **26-week Mastery track**,
which sequences the Learn catalog (50 TypeScript chapters) into gated weeks. The
two share a language, a judge and a type-checker — and almost nothing else,
which is item X-90 below.

**How this document is laid out**

* **Where it stands** — the audit, with numbers.
* **Findings** — defects found during the audit. Fix these before adding content.
* **Decisions** — structural choices to settle before authoring.
* **Part A — Across all six months** — infrastructure, exercise kinds,
  assessment, UI, review loops, analytics, tooling. Everything here lands once
  and pays off in every week.
* **Part B — Month by month** — one list per month, and inside it one block per
  week: chapters, lesson additions, worked examples, pitfalls, exercises, new
  problems, project, exam, quiz, flashcards and month-specific UI.
* **Batching, constraints, and what "done" looks like.**

**Legend** — ✅ shipped · 🚧 partly built · ⬜ planned.
**Priority** — **P0** fix/blocker · **P1** core value · **P2** depth · **P3** polish.
**Size** — S (an hour or two) · M (a day) · L (several days).

---

## Shipped so far

The audit numbers under *Where it stands* are the **before** picture, kept so
the gap stays visible. This is what has landed since.

| | before | now | where |
|---|---|---|---|
| Library problems with a TypeScript starter | 607 of 799, **all 607 failing the judge's own type-check** | **799 of 799, all type-check** | `tools/gen_ts_starters.mjs` → `tools/ts_starters.json` (hash-pinned to the JS it came from); guard: `python tools/verify_ts_starters.py` |
| Function-harness languages | Python, Java | + **TypeScript, JavaScript** | `src-tauri/src/harness.rs`, `stub_ts`/`stub_js` in `gen_seed.py`; 8 new judge tests in `tests/exec_judge.rs` |
| Curated TS-track problems openable in TypeScript | 26 of 85 | **all** (build-asserted) | `_TRACK_RULES` in `mastery_defs.py` |
| Tests per coding final | 2–5 (94 total), hand-typed | **8+ (209 total)**, new ones computed from the reference | `TS_EXAM_MORE_TESTS` in `mastery_defs.py` |
| Proof the finals are right | none — the file cited a verifier that did not exist | **`cargo test --test verify_mastery`**: all 52 finals (both tracks) + every workshop exercise through the real judge | `src-tauri/tests/verify_mastery.rs` |
| Reference-solution bugs | weeks 15 and 19 answered `toString` with a function's source (`name in obj`) | fixed with `Object.hasOwn`, and tested | week 15 / 19 finals |
| Quiz bank per week | 5–10 (170 total), 31 near-duplicate pairs, 4 drawn | **16–18 (424 total)**, duplicates dropped, **8 drawn** | `tools/mastery_ts_quiz.py` |
| Review cards per week | 1 per chapter (name → summary) | **+12 authored per week (312)**, backfilled at launch for weeks already done | `tools/mastery_ts_cards.py`, `commands::backfill_mastery_cards` |
| A place to review cards | **none** — the Flashcards page had been removed, so seeded cards went nowhere | `/flashcards` restored (Markdown, keyboard grading), on Today's "Due now" | `src/pages/Flashcards.tsx` |
| Missed quiz questions | forgotten | **one click turns them into cards** | `QuizPanel` in `Mastery.tsx` |
| Graded practice inside a week | none — week 21 ("Conditional Types & infer") practised a prefix sum | **104 exercises, every week 1–22**: 29 predict-the-type, 20 read-the-error (quoted codes proven), 13 fix-the-bug, 42 type-level challenges | `tools/mastery_ts_practice.py`, kinds `predict`/`diagnose`/`fix`/`typelevel` |
| Error explanations | none | **49-entry TS error glossary**, every example compiler-verified; compile errors link to it | `tools/gen_ts_errors.py` → `src/data/ts_errors.json`, `/ts-errors`, `TsErrorLinks` |
| Editor vs judge | Monaco non-strict with DOM; flagged `import … from "fs"`, missed implicit `any` | **same options and ambient types as the judge**, strictness per exercise | `src/monacoSetup.ts`, `CodeEditor` `tsStrictness` |
| Strictness ladder | every final at plain `strict` — week 14's own "treat every index as possibly missing" final did not compile under the flag it teaches | finals from week 14 run at `strict+indexed` (11 reference solutions fixed); a test proves the preset reaches tsc | `TS_INDEXED_FROM_WEEK` in `mastery_defs.py`, `indexed_strictness_reaches_the_judge` |
| Checkpoint contests | seeded on weeks 13 and 26, but **impossible to take** — the Contest page had been removed and Solve no longer recorded results; a finished checkpoint could never be retaken | `/contest/:id` scoreboard (clock from the stored start), Solve scores `?contest=` submissions, "Start the checkpoint" on the week; **monthly checkpoints** at weeks 4, 8, 17, 22 drawing on the whole month; retakes allowed | `src/pages/Contest.tsx`, `src/lib/contest.ts`, `TS_CONTEST_SLUGS` |
| Interview preparation in the chapters | none | **150 interview questions with model answers** — an "In an interview" section on all 50 TypeScript chapters | `tools/ts_lesson_interview.py` |
| Mastery on Today | absent from "Continue" — the longest track had no resume card | 🎓 card per started track: current week, weeks complete, pace against the start date | `masteryResume` in `src/lib/mastery.ts`, `TrackCards.tsx` |
| Moving to the next problem | carried the previous problem's code, report and stdin over — and autosaved it as the new problem's draft | fresh state per problem; last language kept; pending drafts flushed | `SolveRoute` in `App.tsx`, `Solve.tsx` |

---

## Where it stands

| | now | Java track, for comparison |
|---|---|---|
| Weeks / phases | 26 weeks in 6 phases (4 · 4 · 5 · 4 · 5 · 4) | 26 |
| Learn chapters scheduled | 50, each exactly once (asserted by the build) | — |
| Lesson length | 0.9k–2.1k characters per chapter | — |
| Learn exercises on those chapters | **176** — `drill` and `challenge` only | — |
| Chapters with their own quiz questions | **18 of 50** (3 each) | — |
| Flashcards (`cards`) on TS chapters | **0** | — |
| Curated problem slots | 85 (81 unique) | 134 |
| …of which have a **TypeScript starter** | **26** | — |
| Quiz bank | 170 questions (5–10/week), 4 sampled per sitting | 312 |
| Coding finals | 26, with **2–5 tests** each (94 total) | 26 |
| Checkpoint contests | 2 (weeks 13 and 26) | — |
| Build projects | 26 one-sentence briefs, notes + code saved, **never run or checked** | 26 |

| | |
|---|---|
| Week tables | `tools/mastery_defs.py` → `TS_WEEKS` |
| Advanced chapters | `tools/typescript_mastery.py` (18 chapters) |
| Foundational chapters | `tools/typescript_defs.py`, `tools/typescript_expand.py` (32 chapters) |
| Seed | `src-tauri/seeds/mastery.json`, `src-tauri/seeds/concepts.json` |
| Models | `MasteryWeek`, `MasteryExam`, `MasteryContest`, `MasteryProgress` in `src-tauri/src/models.rs` |
| Progress | `mastery_progress` table (`db.rs`), `repo.rs`, tests in `src-tauri/src/tests.rs` |
| UI | `src/pages/Mastery.tsx` (`WeekCard`, `ProjectPanel`, `QuizPanel`, `ExamPanel`, `CompletionSummary`) |
| Pure logic | `src/lib/mastery.ts` (+ `mastery.test.ts`) — unlock rule, pacing, exam assembly |
| Runtime | Node **24.14** (type stripping) · TypeScript **5.9.3** checker via `tools/ts_typecheck.mjs` |

**The one-line diagnosis.** The *sequence* is good — the order of the 26 weeks
is defensible and the gate (chapters + quiz + judged final) is the right shape.
What is thin is the **volume and variety of practice inside each week**: three
or four fill-in-the-blank drills per chapter, problems most of which can't be
started in TypeScript, and a week-level exam with a handful of tests. The TS
course next door already solved most of this (seven exercise kinds,
type-graded judging, practice families, strictness ladder) and none of it
reaches the Mastery track.

---

## Findings — fix before adding anything

| # | Finding | Evidence | Fix | P |
|---|---|---|---|---|
| ✅ F-01 | **59 of 85 curated problems have no TypeScript starter.** Weeks 1–3, 5, 6, 8, 10, 11, 14, 17 have *zero* TS-startable problems. A TypeScript track whose problems open in Java or Python is broken at the most basic level. | `starter_code` keys per slug; library-wide only 607/799 have `typescript` | Generate TS starters for every slug the track references (and ideally all 192 missing library-wide). Add a build assert in `mastery_defs.py`: every TS-track slug must have a `typescript` starter. | **P0** |
| ✅ F-02 | **Duplicate problem slots.** `group-anagrams-count` (weeks 9 and 13), `valid-anagram` (11 and 13), `subarray-sum-k` (13 and 21), `longest-unique-substring` (13 and 21). | `TS_WEEKS` problem lists | Week 13's reuse is intentional review — mark it (`note: "review"`) and render it as such. Weeks 21's reuse is not; replace. | P1 |
| 🚧 F-03 | **Type-level weeks practise unrelated DSA.** Week 21 (*Conditional Types & infer*) curates a prefix-sum and a sliding-window problem; weeks 18–22 in general can't practise their subject through stdout problems. | week 21 problems | Give weeks 18–22 type-graded problems (X-12) and keep at most one DSA problem as "applied" practice, labelled that way. | P1 |
| ✅ F-04 | **Exam test counts are too low to be a gate.** Week 20 has 2 tests; nine weeks have 3. A final with 2 tests can be passed by special-casing. | `exam.tests` lengths | Minimum 6 tests per final, at least 2 edge cases and 1 "large" case. Build assert. | **P0** |
| ✅ F-05 | **32 of 50 chapters contribute no quiz questions.** The week bank for weeks 1–8 is *only* the 6 authored questions, so with 4 sampled per sitting a learner sees the whole bank in two retakes. | `quiz` per concept | ≥ 8 questions per chapter, ≥ 40 per week bank (X-30). | P1 |
| ✅ F-06 | **No flashcards on any TypeScript chapter.** Completing a week is supposed to feed flashcards and revision, but TS chapters carry `cards: []`. | concepts.json | ≥ 12 cards per chapter (X-50). | P1 |
| ✅ F-07 | **Only two exercise kinds.** 176 exercises, all `drill` or `challenge`. `predict`, `diagnose`, `retype`, `design`, `fix` and `judge_mode: "types"` exist in the same codebase and the same judge. | concepts.json kinds | X-10 to X-14. | P1 |
| ⬜ F-08 | **Projects are never executed.** The brief is one sentence; the code box is saved but never run, and "shipped" is a self-declared tick. | `ProjectPanel` | X-40 to X-46. | P1 |
| ⬜ F-09 | **Week 26 has the smallest quiz bank (5)** and it is the capstone week. Week 25 packs **four** chapters into one week (errors, error types, async, async patterns). | `TS_WEEKS` | Decision D-2. | P1 |
| ✅ F-10 | **Week 14's project asks you to turn on `noUncheckedIndexedAccess` "in your head".** The judge already supports per-exercise strictness presets (`strictness: "strict+indexed"`). | week 14 `project` | Make it real: the week-14 final and exercises run under `strict+indexed`. | P2 |
| ✅ F-11 | **Week 13 schedules no chapters**, so its bank has no chapter questions to draw on beyond the 6 authored ones. | week 13 `concepts: []` | Use `quiz_from` to pull from weeks 9–12 (the mechanism already exists). | P2 |
| ⬜ F-12 | **Lessons stop at the syntax.** 0.9–2.1k characters is a page. There is no "why this exists", no failure-mode gallery, no interview angle, no "what the compiler actually says". | concepts.json `lesson` | Lesson template X-02. | P1 |

---

## Decisions — settle before authoring

### D-1. One TypeScript curriculum or two?
The app has two TypeScript curricula written for different people — the Course
for a beginner, Mastery for someone going deep. **Recommendation: keep both,
and make Mastery *reuse* Course exercises by reference** rather than re-authoring
them (X-90). A Mastery week gets a "From the course" practice section pointing
at the matching course lessons and practice families.

### D-2. Rebalance the back half without changing 26
Week 25 carries four chapters; week 13 carries none; modules and declaration
files are squeezed into the capstone week. **Recommended shape:**

| week | now | proposed |
|---|---|---|
| 11 | Narrowing & Type Guards | Narrowing, Type Guards **& Nullish** (move `ts_nullish` here — it *is* narrowing) |
| 13 | Checkpoint — Consolidation | **Tuples, Overloads & Function Types in Depth** + the checkpoint contest stays attached |
| 14 | Nullability & Compiler Strictness | **The Toolchain: tsconfig, Modules & Declarations** (`ts_tsconfig`, `ts_modules`, `ts_declaration_files`) |
| 25 | Errors & Async | **Errors, Result & Resource Management** |
| 26 | Modules, Declarations & Capstone | **Async, Concurrency & Cancellation** |
| 27 *(optional, ungated)* | — | **Capstone & Mock Interview Week** — same pattern as the DSA curriculum's optional stage 8 |

The build's "every chapter exactly once" assert still holds; it just holds over
a better distribution.

### D-3. Where type-level work is graded
Months 4–5 are mostly about types, which stdout cannot test. **Decision:
`judge_mode: "types"` becomes a first-class Mastery grading mode** — for
exercises, for problems (a new problem kind, X-12) and for the coding final of
weeks 18–22 (a final can be a set of `Expect<Equal<…>>` assertions the learner's
types must satisfy, plus a small runtime part).

### D-4. Which TypeScript version the programme teaches
The checker is 5.9.3. **TypeScript 6.0** is the JavaScript-based bridge release
that deprecates options ahead of **TypeScript 7** (the native, Go-based
compiler). Decision: upgrade the checker once 6.x is stable in `node_modules`,
re-run every verifier, and teach the deprecations as content in week 14 (see
M4). *Check every specific flag change against the official release notes
before writing prose about it — don't author from memory.*

### D-5. Erasable syntax is a rule, not an accident
The runner strips types. `enum`, `namespace`, parameter properties and
legacy/standard decorators **cannot run**. Anything teaching them is
type-graded, and the lessons say *why* (`--erasableSyntaxOnly`). Same rule as
the TS course (decision 5 in `TS_ROADMAP.md`).

---

# Part A — Across all six months

Everything here is built once and then used by every week in Part B.

### A1. Content model & lesson quality

| # | Item | P | Size |
|---|---|---|---|
| X-01 | Split `mastery_defs.py`'s TS weeks into `tools/mastery_ts_m1.py` … `mastery_ts_m6.py` (one per month), exec'd in order — the same split that took `typescript_course.py` from 15,900 lines to 672. Verify by hashing `mastery.json` before/after: must be byte-identical. | P1 | M |
| X-02 | **Lesson template** for every chapter, enforced by a lint: *Why it exists* → *The core idea* → *Worked example* → *What the compiler says* (a real `TSnnnn` message, verified) → *Pitfalls* (≥ 3) → *In an interview* → *Where it shows up later* (forward links). | P1 | L |
| X-03 | Raise every lesson to **4–8k characters** — roughly 15–25 minutes of reading. Today's lessons are a quarter of that. | P1 | L |
| X-04 | `examples` field per chapter: 3–6 runnable worked examples, each openable in a scratch editor with one click ("Run this"). | P1 | M |
| X-05 | `pitfalls` field per chapter: short "this looks right but…" cases, each with the wrong code, the symptom, and the fix. Rendered as collapsible cards. | P1 | M |
| ✅ X-06 | `interview` field per chapter: 3–5 questions an interviewer actually asks about the topic ("`any` vs `unknown` vs `never`?", "`interface` vs `type`?"), with model answers. | P1 | M |
| X-07 | `errors` field per chapter: the 3–5 `TSnnnn` codes a learner will hit in this chapter, verified against `ts_typecheck.mjs`, feeding a global error glossary (X-66). | P1 | M |
| X-08 | Chapter **cheat sheet** (one screen, printable) and **glossary** entries, as the TS course already has per week. | P2 | M |
| X-09 | "Compared with Java" notes (`java` field exists) rewritten to cover Python and JavaScript too — the learner may arrive from any of them. | P3 | M |

### A2. Exercise kinds — bring the Course's toolkit to Mastery

| # | Item | P | Size |
|---|---|---|---|
| 🚧 X-10 | Port the four reading kinds to Learn/Mastery: **`predict`** (what type is inferred?), **`diagnose`** (what caused this `TSnnnn`?), **`retype`** (it runs and its types say nothing — make them honest), **`design`** (write the type first). Target **≥ 3 of each per chapter**. | P1 | L |
| 🚧 X-11 | **`fix`** (the starter compiles and prints the wrong thing, or crashes) — ≥ 2 per chapter. | P1 | M |
| 🚧 X-12 | **Type-graded problems** (`judge_mode: "types"`): a Library problem whose "tests" are `Expect<Equal<…>>` assertions. Needs: `judge_mode` accepted on problems, the harness appended at check time, and TestResults showing *which* assertion failed. Unlocks months 4–5. | **P0** for M4–M5 | L |
| X-13 | **`refactor`** — given working code, change it to satisfy a constraint (remove every `any`, make it immutable, replace the if-chain with a lookup) while tests still pass; banned-token list enforces the constraint. | P2 | M |
| X-14 | **`explain`** — ungraded free-text answer, compared on reveal against a model answer; used for "why" questions and fed into self-review. | P3 | S |
| X-15 | **`order`** — drag lines of a program into the correct order (Parsons problem). Excellent for months 1–2 and for async ordering in month 6. | P2 | M |
| X-16 | **`spot`** — click the line that is the bug / the line where the type narrows / the line that throws. | P2 | M |
| 🚧 X-17 | **Strictness ladder** for Mastery: chapter-level `strictness` default (`strict` → `strict+indexed` from week 11) so indexed access is honest everywhere after narrowing is taught. | P1 | S |
| X-18 | **Progressive hint ladders** (`hints: [nudge, strategy, near-answer]`) on every exercise — the field exists and is barely used in Mastery. | P2 | M |
| X-19 | **Practice families** on Learn chapters: five variations of one pattern, twisting one dimension at a time, outside the gate. Target 4 families × 5 per chapter. | P2 | L |

### A3. Problems

| # | Item | P | Size |
|---|---|---|---|
| ✅ X-20 | TS starters for all 81 curated slugs (F-01), then the other ~110 library problems still missing one. | **P0** | M |
| X-21 | Raise curated problems to **12–16 per week** (from 2–5), tiered *Warm-up / Core / Stretch*, ~380 slots total. Month-by-month lists in Part B. | P1 | L |
| X-22 | **"Idiomatic TypeScript" editorial** on every curated problem: not just the algorithm, but the types — how `Map<K,V>` vs `Record`, `readonly` inputs, a discriminated-union result, `noUncheckedIndexedAccess`-safe indexing would look in a model answer. | P1 | L |
| ✅ X-23 | **Function-harness problems for TypeScript** — `harness.rs` generates I/O glue for Python and Java only. Add TS so a problem can say "implement `groupBy(xs, key)`" without stdin parsing. The TS course's hidden `harness` driver is the model. | P1 | L |
| 🚧 X-24 | **Type-challenge bank** (with X-12): ~120 original type-level puzzles, easy → extreme, used by weeks 15–22 and as optional daily reps. | P1 | L |
| X-25 | Tag every problem with the week that first makes it solvable (`min_week`) and show "you can solve this now" in the Library when browsing from Mastery. | P2 | M |
| X-26 | "Same problem, three ways" sets — one problem solved imperatively, functionally and with a class, all judged, compared in the editorial. | P3 | M |

### A4. Assessment — quiz, exam, checkpoints

| # | Item | P | Size |
|---|---|---|---|
| 🚧 X-30 | Week quiz bank **≥ 40 questions**; sample **10** per sitting (from 4). Mixed kinds: MCQ, "what does this print", "which line errors", "which type is inferred". ~1,050 questions total. | P1 | L |
| X-31 | New quiz question types: **code-output** (show code, pick the output), **type-inference** (pick the inferred type), **multi-select**, **fill-the-type** (typed short answer checked by `ts_typecheck.mjs`). | P1 | L |
| 🚧 X-32 | Every coding final: **≥ 6 tests**, ≥ 2 edge cases, 1 large input, and a **hidden** set not shown until pass (F-04). | **P0** | M |
| X-33 | **Alternate finals**: a second final per week, served on retake, so a failed final can't be passed by memorising the first. | P2 | L |
| X-34 | **Two-part finals** for weeks 15–22: a type-graded half (assertions) + a runtime half (stdout). Pass requires both. | P1 | M |
| 🚧 X-35 | **Monthly checkpoint** at the end of every month (today: only weeks 13 and 26) — a timed contest from that month's problems + a 20-question mixed quiz. Months 1, 2, 4, 5 gain one. | P1 | M |
| X-36 | **Final exam** for the whole programme: 3 hours, 5 coding problems across months, 40 questions, a type-challenge section. Unlocks a completion summary (X-68). | P2 | L |
| X-37 | Quiz **explanations for wrong options**, not just the right one ("why not B?"). | P2 | M |
| X-38 | Question-level analytics: track per-question accuracy; flag questions everyone gets right (too easy) or wrong (probably ambiguous) in a dev view. | P3 | M |

### A5. Build projects

| # | Item | P | Size |
|---|---|---|---|
| X-40 | Replace one-sentence briefs with **structured briefs**: goal · requirements (numbered) · stretch goals · "done when" checklist · sample input/output. | P1 | L |
| X-41 | **Run the project** — the code box gets Run and Test buttons backed by `run_scratch`, with 5–10 acceptance tests per project. "Shipped" requires them green. | P1 | M |
| X-42 | **Self-review rubric** per project (typing quality, no `any`, error handling, naming) — tick-boxes saved with the project. | P2 | S |
| X-43 | **Reference implementation** revealable after shipping, with a side-by-side diff against the learner's code (`src/lib/diff.ts` already does LCS). | P2 | M |
| X-44 | **Project continuity** — a single running project that grows each month (like the Course's Budget Buddy): *Ledger → typed CLI → validated store → type-safe event system → async loader*. The monthly "arc" projects are listed in Part B. | P1 | L |
| X-45 | **Multi-file projects** in the project workspace (tabs for several `.ts` files, bundled into one file for the judge by concatenation with `export` stripped). Required for months 4 and 6. | P2 | L |
| X-46 | Project history — keep every saved version, not just the latest (ProjectHistory.tsx exists for the Projects track and can be reused). | P3 | M |

### A6. UI — the Mastery page and the editor

| # | Item | P | Size |
|---|---|---|---|
| X-60 | **Week view redesign**: a checklist spine down the left (Read → Practise → Problems → Project → Quiz → Final), each step with a count and a state; content on the right. | P1 | L |
| 🚧 X-61 | **Today card** on the Mastery page: "at your pace, today is: finish chapter 2, 3 drills, 1 problem" — derived from pacing + remaining work. Also surfaced on the Today page (`today.ts`). | P1 | M |
| ✅ X-62 | **Inferred-type hovers in the editor** — Monaco ships a TypeScript language service; wire it for TS exercises so hovering shows the inferred type (with `strict` and the exercise's strictness preset). The single biggest learning aid for this language. | P1 | M |
| ✅ X-63 | **Inline error squiggles with explanations** — show `TSnnnn` diagnostics live, and on hover link to the error glossary entry (X-66). | P1 | M |
| X-64 | **"What runs" view** — a toggle showing the type-stripped JavaScript that actually executes, lines aligned with the source. Makes erasure visible from week 1. | P2 | M |
| X-65 | **Strictness switcher** in scratch mode — flip `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes` and watch errors appear and disappear. | P2 | M |
| ✅ X-66 | **TS error glossary** page (`/ts-errors`): every `TSnnnn` code the programme can produce, plain-English cause, minimal repro, fix, and which chapters teach it. | P1 | M |
| X-67 | **Type playground** (`/playground/ts`): scratch file + panel listing every declared type's fully-expanded form (via the language service's `quickInfo`). | P2 | L |
| X-68 | **Completion summary** per month and for the programme: time spent, finals first-try rate, weakest chapters, projects shipped, printable. | P2 | M |
| X-69 | **Skill radar** — per-phase mastery (reading types, writing types, runtime correctness, async, type-level) computed from exercise kinds passed. | P3 | M |
| ✅ X-70 | **Quiz review screen** after every sitting: every question, your answer, the right answer, the explanation, "add to flashcards". | P1 | S |
| X-71 | **Exam timer & focus mode** (optional): hide the sidebar, show elapsed time, record it; does not gate. | P2 | S |
| X-72 | **Keyboard-first flow**: `j/k` through exercises, `Ctrl+Enter` run, `Ctrl+Shift+Enter` submit, `h` next hint, `n` next unfinished item. | P2 | S |
| X-73 | **Search inside Mastery** — find a chapter, example, pitfall or error code across all 26 weeks. Command palette integration. | P2 | M |
| X-74 | **Week notes** — a free-form notes area per week (separate from project notes) exported with the backup. | P3 | S |
| X-75 | **Locked-week preview** — sealed weeks show their title, goal and chapter list (not content), so the learner can see where the programme goes. | P3 | S |
| X-76 | Phase banners with month goals and a progress ring per month. | P3 | S |

### A7. Review loops — spaced repetition and weakness

| # | Item | P | Size |
|---|---|---|---|
| 🚧 X-50 | **Flashcards for every chapter** — ≥ 12 per chapter (definition, "what does this infer", "which error", "fix this line"), ~1,000 total, fed to the revision queue when a week completes. | P1 | L |
| ✅ X-51 | **Missed-question recycling**: a wrong quiz answer creates a flashcard automatically. | P1 | S |
| X-52 | **Failed-exercise re-queue**: an exercise failed ≥ 2 times re-appears in a later week's warm-up. | P2 | M |
| X-53 | **Interleaved review weeks** — each week's warm-up draws 3 exercises from two and five weeks earlier. | P1 | M |
| X-54 | **Weak-chapter detector** — first-try rate + hints used per chapter → "revisit these" list on the Mastery page. | P2 | M |
| X-55 | **Review mode for completed weeks**: a 15-minute mixed session drawn from everything behind you. | P2 | M |

### A8. Analytics & pacing

| # | Item | P | Size |
|---|---|---|---|
| X-80 | Per-week **time budget** (e.g. 8–10 h) displayed next to actual study time; flag weeks that took 2× budget. | P2 | S |
| X-81 | Pacing that understands **pauses** (a "holiday" toggle stops the clock). | P2 | S |
| X-82 | "What slowed you down" — per week: most-failed exercise, most-hinted chapter, slowest final. | P3 | M |
| X-83 | Export progress as JSON/Markdown for a portfolio or a mentor. | P3 | S |

### A9. Integration with the rest of the app

| # | Item | P | Size |
|---|---|---|---|
| X-90 | **Course ↔ Mastery links** (D-1): every Mastery week lists the TS course lessons and practice families that cover the same ground, with completion shown. | P1 | M |
| X-91 | **DSA ↔ Mastery**: months 3 and 6 link the DSA curriculum units whose problems use the same data structures (Maps & Sets → hashing unit; generic DS → structures stage). | P2 | S |
| X-92 | **Projects track ↔ Mastery**: month 6 recommends the Backend Lab / Todo API modules as the next step. | P3 | S |
| X-93 | Mastery completion writes to the **heatmap**, **streak** and **Today** exactly like other tracks (already partly true for study time). | P2 | S |

### A10. Tooling & verification

| # | Item | P | Size |
|---|---|---|---|
| 🚧 X-100 | **Build asserts** in `mastery_defs.py`: TS starter exists for every curated slug; ≥ 6 final tests; ≥ 40-question bank; ≥ 12 cards per chapter; no slug curated twice except where `note` starts with "review"; every lesson passes the template lint. | **P0** | S |
| ✅ X-101 | **A Mastery verifier** — `cargo test --test verify_mastery`: runs every final's reference solution through the real judge, every exercise's solution, every project's reference, every type-graded assertion. Mirrors `verify_ts_course.rs`. | **P0** | M |
| X-102 | `--only=wNN` fast path for authoring, as the course verifier has. | P1 | S |
| ✅ X-103 | Diagnose-prompt checker: every quoted `TSnnnn` is re-derived from the starter (the course's verifier caught four wrong codes on first try — see the table in `TS_ROADMAP.md`). | P1 | S |
| X-104 | Scope lint for Mastery — nothing may use a construct a later week teaches (port `_SCOPE_RULES`). | P1 | M |
| X-105 | Upgrade the checker to TypeScript 6.x (D-4), re-run every verifier, record deltas. | P2 | M |
| X-106 | Content stats script — prints the "Where it stands" table from the seed so this document never goes stale. | P3 | S |

---

# Part B — Month by month

Each month lists the weeks it contains, then per week: **Chapters** (existing
✅ / new ⬜), **Lesson additions**, **Worked examples**, **Pitfalls**,
**Exercises**, **New problems** (original, all with TypeScript starters, one
line each — slug · what it asks), **Project**, **Final**, **Quiz** and
**Cards**. Counts are targets.

New chapter keys follow `ts_*` and are scheduled exactly once (the build
assert). Numbering: `M1-01`… are the month's own non-week items.

---

## Month 1 — Language Foundations (weeks 1–4)

**Month goal:** write small, correct, fully-typed programs that read stdin and
print stdout, and know exactly what TypeScript infers without being told.

**Month-level items**

| # | Item | P |
|---|---|---|
| M1-01 | **Onboarding week 0** (ungated, 30 min): the editor, Run vs Submit, how stdin/stdout grading works, reading a failing test, hovering for types. | P1 |
| M1-02 | **stdin/stdout visualiser** — show the test's stdin split into lines, what your program printed, and where the first difference is, character-aligned. | P1 |
| M1-03 | "**Predict first**" mode for months 1–2: before Run, you must type what you think it prints; mismatches are logged as learning moments. | P2 |
| 🚧 M1-04 | **Month 1 checkpoint** (new, X-35): 60-minute contest of 4 problems + 20 questions. | P1 |
| M1-05 | Month arc project start: **`ledger.ts` v1** — read transactions line by line, print a formatted statement. Grows every month (X-44). | P1 |

### Week 1 — Values, Types & Inference
*Now:* `ts_variables`, `ts_types`, `ts_inference` · 4 problems · 6 quiz · final "Temperature table" (4 tests).

* **Chapters:** ✅ the three above · ⬜ **`ts_program_io`** — the stdin/stdout contract: `readFileSync(0)`, `trim`, `split("\n")`, `Number()` vs `parseInt`, printing with `console.log` and template strings.
* **Lesson additions:** literal types from `const` vs widening from `let`; `number` is one type (no int/float); `null` vs `undefined`; `any` as a hole in the type system; `unknown` as the safe top type; why annotations on locals are usually noise and on function boundaries usually essential; how type stripping means types never change runtime behaviour.
* **Worked examples:** celsius converter with and without annotations (same output — types are erased); `let x = 5` hover vs `const x = 5` hover; reading two numbers on one line vs two lines.
* **Pitfalls:** `Number("")` is `0`; `Number("12px")` is `NaN`; `parseInt("08")` works but `parseInt("1e3")` is `1`; forgetting `trim()` leaves `"\r"` on Windows input; `console.log(a, b)` inserts a space.
* **Exercises:** +8 drill, +4 predict ("what does the compiler infer?"), +3 diagnose (TS2322 assigning string to number, TS2588 reassigning a `const`, TS7006 implicit any on a parameter), +2 fix, +1 retype.
* **New problems (12):**
  `sum-of-line` · sum all numbers on one line ·
  `min-max-line` · print the min and max of a line ·
  `kelvin-to-all` · convert K to C and F to 2 dp ·
  `seconds-to-hms` · seconds → `H:MM:SS` ·
  `bmi-calculator` · two numbers → BMI to 1 dp ·
  `swap-two-values` · read two, print swapped ·
  `circle-stats` · radius → circumference and area to 3 dp ·
  `average-of-three` · three numbers → mean ·
  `split-bill` · total, people, tip % → per-person to the cent ·
  `integer-division` · quotient and remainder, including negatives ·
  `hours-to-days` · hours → days and remaining hours ·
  `echo-typed` · echo each line prefixed by `number:`/`text:` depending on whether it parses.
* **Project:** `units.ts` → structured brief with 6 acceptance tests; stretch: a lookup table of conversions keyed by unit name.
* **Final:** Temperature table → 7 tests incl. negatives, `-40`, fractional input.
* **Quiz:** +34 (literal vs widened types, `any`/`unknown`, parsing numbers, what `console.log` prints for `undefined`/`null`/`NaN`).
* **Cards:** 36.

### Week 2 — Operators & Control Flow
*Now:* `ts_operators`, `ts_conditionals` · 5 problems · final "Ticket price".

* **Chapters:** ✅ both · ⬜ **`ts_equality`** — `===` vs `==`, `NaN !== NaN`, `Object.is`, the full truthiness table, `??` vs `||`.
* **Lesson additions:** precedence of `&&`/`||`/`??` (and why mixing `??` with `||` without parentheses is a syntax error); `switch` fallthrough and `break`; ternaries for values, `if` for effects; early returns; comparing strings (`"10" < "9"`); `%` with negatives.
* **Worked examples:** leap-year rule three ways (nested ifs, single boolean expression, lookup); ticket pricing with a table of age bands; grading with a `switch (true)` vs an if-chain.
* **Pitfalls:** `if (count)` skipping 0; `value || default` replacing `0`/`""`; `==` coercions (`"" == 0`); `-7 % 3 === -1`; a `switch` missing `break`.
* **Exercises:** +8 drill, +3 predict, +3 diagnose (TS2367 comparison with no overlap, TS2365 operator on wrong types, TS7029 fallthrough under `noFallthroughCasesInSwitch`), +3 fix, +2 order (Parsons).
* **New problems (12):** `grade-letter` · `tax-bracket` · `triangle-kind` (equilateral/isosceles/scalene/invalid) · `quadrant-of-point` · `day-of-week-name` · `shipping-cost` (weight bands) · `is-weekend` · `compare-versions-simple` (`1.2` vs `1.10`) · `water-state` (temp → solid/liquid/gas) · `fizzbuzz-line` · `clamp-value` · `sign-of-product` (without multiplying).
* **Project:** `grade.ts` — if-chain version + table version, 8 tests, rubric item "the table version needs no code change to add a grade".
* **Final:** Ticket price → 7 tests incl. boundary ages.
* **Quiz:** +34 (truthiness, precedence, `??`, `switch`). **Cards:** 32.

### Week 3 — Loops & Numbers
*Now:* `ts_loops`, `ts_number_math` · final "Number report".

* **Chapters:** ✅ both · ⬜ **`ts_number_format`** — floating point (`0.1 + 0.2`), `toFixed` rounding, integers as cents, `Number.isInteger`, `Number.MAX_SAFE_INTEGER`, **`bigint`** (`123n`), `Intl.NumberFormat` for currency and grouping.
* **Lesson additions:** `for` / `while` / `do…while` / `for…of`; `break`/`continue` and labelled breaks; loop invariants in plain English; off-by-one as a habit, not an accident; `Math.floor` vs `Math.trunc` for negatives; integer overflow doesn't exist — precision loss does.
* **Worked examples:** digit sum with `%` and division; primes by trial division to `√n`; running totals in cents; factorial past 2^53 with `bigint`.
* **Pitfalls:** `(1.005).toFixed(2)` is `"1.00"`; `Math.round(-2.5)` is `-2`; `for (const i in arr)` gives strings; mutating a loop bound mid-loop.
* **Exercises:** +8 drill, +3 predict, +3 diagnose (TS2362/2363 arithmetic on non-numbers, mixing `bigint` and `number` TS2365), +3 fix, +2 spot (the off-by-one line).
* **New problems (12):** `collatz-steps` · `digital-root` · `gcd-lcm` · `perfect-number` · `armstrong-number` · `reverse-integer` · `sum-of-multiples` · `big-factorial` (bigint) · `fibonacci-nth-big` (bigint) · `count-primes-upto` · `number-in-words-small` (0–999) · `compound-interest-cents`.
* **Project:** `stats.ts` — one pass, no array methods, 8 tests including an empty line.
* **Final:** Number report → 7 tests incl. single value and all-equal.
* **Quiz:** +34. **Cards:** 34.

### Week 4 — Text & String Methods
*Now:* `ts_strings`, `ts_string_methods` · final "Title case and initials".

* **Chapters:** ✅ both · ⬜ **`ts_regex`** — literals vs `new RegExp`, flags, `test`/`match`/`matchAll`/`replaceAll`, named groups, `RegExp.escape` · ⬜ **`ts_unicode`** — UTF-16 code units, `for…of` iterates code points, `"é".length`, emoji, `Intl.Segmenter` for graphemes, `localeCompare`.
* **Lesson additions:** strings are immutable; `slice` vs `substring`; `padStart` for tables; `split("")` breaks emoji; template literal multi-line; building strings in loops vs `join`.
* **Worked examples:** slugify three ways (loop, chained methods, regex); a fixed-width table printer; counting words with and without regex; parsing `key=value` pairs with named groups.
* **Pitfalls:** `replace` with a string replaces only the first match; `split(" ")` on double spaces; `toUpperCase` on `ß`; sorting strings with `<` vs `localeCompare`.
* **Exercises:** +8 drill, +3 predict, +3 diagnose (TS2339 method on possibly-undefined match result, TS2532), +3 fix, +2 refactor ("no loops — string methods only").
* **New problems (12):** `longest-word` · `capitalize-sentences` · `acronym` · `is-pangram` · `compress-spaces` · `mask-card-number` · `count-substrings` · `camel-to-snake` · `snake-to-camel` · `extract-emails` (regex) · `roman-to-int` · `justify-line` (pad to width).
* **Project:** `slug.ts` — 8 tests incl. unicode and leading/trailing punctuation.
* **Final:** Title case and initials → 7 tests.
* **Quiz:** +34. **Cards:** 34.
* **Month 1 UI:** stdin/stdout visualiser (M1-02) and inferred-type hovers (X-62) must land *before* month 1 content ships — they are the teaching tools for these four weeks.

---

## Month 2 — Functions & Data (weeks 5–8)

**Month goal:** design small functions with honest signatures, transform
collections without mutation surprises, and model records as typed objects.

**Month-level items**

| # | Item | P |
|---|---|---|
| M2-01 | **TypeScript function harness** (X-23) must be live by week 5 — from here, most problems say "implement `f`", not "parse stdin". | **P0** |
| M2-02 | **Call-stack visualiser** for closures and recursion (extends `/debugger`): step through, see frames and captured variables. | P2 |
| M2-03 | **Array-method pipeline viewer** — for a `.filter().map().reduce()` chain, show the intermediate array after each step. | P2 |
| M2-04 | **Month 2 checkpoint** (new): 75-minute contest, 4 problems + 20 questions. | P1 |
| M2-05 | Arc project: **`ledger.ts` v2** — transactions become typed objects; filter/group/summarise with array methods; a `formatMoney` with options. | P1 |

### Week 5 — Functions & Parameters
*Now:* `ts_functions`, `ts_params` · 4 problems · final "Formatter with options".

* **Chapters:** ✅ both · ⬜ **`ts_overloads`** — overload signatures vs implementation signature, when a union parameter is better, `this` parameters · ⬜ **`ts_closures_scope`** — lexical scope, closures, the loop-closure bug with `var`, IIFEs, module scope.
* **Lesson additions:** return type inference vs annotation (annotate exported functions); optional vs default parameters; rest parameters as tuples; `void` vs `undefined` returns; function declarations vs arrow functions (hoisting, `this`); pure functions.
* **Worked examples:** `formatMoney(cents, { symbol, decimals })` with an options object; a counter factory via closure; overloads for `parse(input: string): number` / `parse(input: string[]): number[]`.
* **Pitfalls:** default parameter evaluated each call; optional before required (TS1016); a callback typed `() => void` still accepts a function returning a value; forgetting `return` in a braced arrow.
* **Exercises:** +8 drill, +3 predict, +3 diagnose (TS2554 wrong arity, TS2394 overload incompatible, TS7011), +3 fix, +2 design.
* **New problems (12, harness-based):** `make-counter` · `once` (call a function at most once) · `memoize-unary` · `compose-two` · `default-greeting` · `safe-divide` (returns `number | null`) · `sum-rest` · `pluralize` · `format-duration` · `range-array` (start, end, step with defaults) · `apply-n-times` · `curry-add3`.
* **Project:** `format.ts` — 10 tests over option combinations.
* **Final:** Formatter with options → 8 tests.
* **Quiz:** +34. **Cards:** 34.

### Week 6 — Higher-Order Functions
*Now:* `ts_higher_order` · 3 problems · final "Compose a text pipeline".

* **Chapters:** ✅ `ts_higher_order` · ⬜ **`ts_recursion`** — base case, recursive case, the call stack, recursion depth in Node, recursion vs loops, simple memoisation (moved forward from week 25 of the course arc so month 6 isn't the first time the learner sees it).
* **Lesson additions:** functions as values; typing callbacks with contextual typing; `pipe` vs `compose`; partial application and currying; generics appear here *by necessity* for `pipe` — a preview, not the lesson (week 18 is).
* **Worked examples:** `pipe(trim, lower, collapseSpaces, slug)`; a debounce-shaped function (simulated clock, deterministic); recursive `sumDigits`, `power`, `flatten`.
* **Pitfalls:** passing `parseInt` to `map` (`["1","2","3"].map(parseInt)`); losing `this` when passing a method; unbounded recursion (`RangeError: Maximum call stack size exceeded`).
* **Exercises:** +8 drill, +3 predict, +3 diagnose (TS2345 callback parameter mismatch), +3 fix, +2 order.
* **New problems (12):** `pipe-strings` · `apply-pipeline-ops` (ops from stdin) · `count-by-predicate` · `find-first-index` · `every-some` · `recursive-sum-digits` · `recursive-power` · `flatten-nested` · `hanoi-moves` · `permutations-count` · `binary-strings-n` · `memo-fib`.
* **Project:** `pipeline.ts` — 8 tests; stretch: `pipe` with a typed variadic signature.
* **Final:** Compose a text pipeline → 8 tests.
* **Quiz:** +33. **Cards:** 30.

### Week 7 — Arrays & Array Methods
*Now:* `ts_arrays`, `ts_array_methods` · final "Array statistics".

* **Chapters:** ✅ both · ⬜ **`ts_tuples`** — tuples, labelled elements, optional and rest elements, `readonly` tuples, returning tuples · ⬜ **`ts_array_modern`** — `at`, `toSorted`/`toReversed`/`toSpliced`/`with` (non-mutating), `Object.groupBy`, `flatMap`, `Array.from({ length })`, `structuredClone`.
* **Lesson additions:** `T[]` vs `Array<T>`; `sort()` mutates and sorts as strings by default; `reduce` with an explicit accumulator type; `find` returns `T | undefined`; `includes` vs `indexOf`; `noUncheckedIndexedAccess` preview.
* **Worked examples:** statistics with `reduce`; `toSorted` vs `sort` side-by-side (showing the original array); grouping transactions by category with `Object.groupBy`; `[min, max]` tuple return.
* **Pitfalls:** `[10, 9, 1].sort()` → `[1, 10, 9]`; `reduce` without an initial value on an empty array throws; `new Array(3).map(...)` does nothing (holes); `forEach` can't `break`.
* **Exercises:** +10 drill, +3 predict, +3 diagnose (TS2769 reduce overload, TS2493 tuple index out of range), +3 fix, +2 refactor ("no mutation").
* **New problems (14):** `chunk-array` · `zip-arrays` · `unzip-pairs` · `rotate-left-k` · `remove-duplicates-keep-order` · `pairwise-diff` · `sliding-max-k-small` · `transpose-matrix` · `group-by-length` · `min-max-tuple` · `sort-by-two-keys` · `top-n-scores` · `interleave` · `cumulative-product`.
* **Project:** `table.ts` — 8 tests.
* **Final:** Array statistics → 8 tests incl. single element and duplicates.
* **Quiz:** +34. **Cards:** 40.

### Week 8 — Destructuring, Objects & JSON
*Now:* `ts_destructuring`, `ts_objects`, `ts_json` · 3 problems · final "Merge JSON records".

* **Chapters:** ✅ all three · ⬜ **`ts_interfaces_types`** — `interface` vs `type`, `extends`, declaration merging, when each wins · ⬜ **`ts_index_signatures`** — `{ [key: string]: T }`, `Record<K, V>`, excess-property checks, optional properties vs `| undefined` (`exactOptionalPropertyTypes`).
* **Lesson additions:** shorthand properties; computed keys; spread and its shallowness; `Object.keys` returns `string[]` (and why); `JSON.parse` returns `any` — the reason week 11 exists; `JSON.stringify` with indentation and replacers; dates in JSON.
* **Worked examples:** config reader with defaults via destructuring; merging records with spread (later keys win); `Object.entries` round trip; pretty-printing JSON with sorted keys.
* **Pitfalls:** spreading `undefined` is fine, spreading `null` is fine, destructuring `null` throws; nested spread is shallow; `JSON.stringify` drops `undefined` and functions; `Object.keys` order for integer-like keys.
* **Exercises:** +10 drill, +3 predict, +4 diagnose (TS2353 excess property, TS2561, TS2741 missing property, TS7053 implicit any from string index), +3 fix, +2 design.
* **New problems (12):** `merge-configs-deep` · `pick-fields` · `invert-object` · `count-by-key` · `flatten-object-paths` (`a.b.c`) · `unflatten-paths` · `diff-objects` · `json-pretty-sorted` · `rename-keys` · `object-to-query-string` · `validate-required-fields` · `nested-get-with-default`.
* **Project:** `config.ts` — 8 tests; **arc:** `ledger.ts` v2 due.
* **Final:** Merge JSON records → 8 tests.
* **Quiz:** +34. **Cards:** 40.

---

## Month 3 — The Type System (weeks 9–13)

**Month goal:** model data so illegal states are unrepresentable, and read
control-flow narrowing the way the compiler does.

**Month-level items**

| # | Item | P |
|---|---|---|
| M3-01 | **Narrowing stepper** — step through a function; at each line, a side panel shows the narrowed type of each variable (via the language service's `quickInfo` at that position). The teaching tool for weeks 10–12. | P1 |
| M3-02 | **Exhaustiveness badge** — the editor shows "switch is exhaustive ✓" when a `never` check compiles. | P3 |
| M3-03 | **State-machine diagram** — for a union of states + transition function, render the states and allowed transitions (weeks 10 and 12). | P3 |
| M3-04 | **Strictness ladder step**: from week 11, every exercise runs under `strict+indexed` (X-17). Announce it in-app. | P1 |
| M3-05 | Arc project: **`ledger.ts` v3** — transactions become a discriminated union (`deposit` / `withdrawal` / `transfer`), parsed from JSON with a guard, exhaustive formatting. | P1 |

### Week 9 — Maps, Sets & Hashing
*Now:* `ts_maps_sets` · 5 problems · final "Inverted index".

* **Chapters:** ✅ `ts_maps_sets` · ⬜ **`ts_set_algebra`** — ES2025 `Set` methods (`union`, `intersection`, `difference`, `symmetricDifference`, `isSubsetOf`), `Map.groupBy`, `WeakMap`/`WeakSet` and when identity keys matter.
* **Lesson additions:** `Map` vs object (any key type, insertion order, `size`, no prototype keys); `get` returns `V | undefined`; counting pattern `m.set(k, (m.get(k) ?? 0) + 1)`; object keys by identity; iteration order guarantees; hashing intuition — why lookup is O(1) on average.
* **Worked examples:** word frequency; two-sum with a `Map`; de-duplicating objects by id; tag intersection with `Set.prototype.intersection`.
* **Pitfalls:** `map[key]` on a `Map` (sets a property, not an entry); two identical object literals are different keys; `JSON.stringify(new Map())` is `{}`; `new Set("abc")` is a set of characters.
* **Exercises:** +8 drill, +3 predict, +3 diagnose (TS2532 on `get()`), +3 fix, +2 refactor ("replace the object lookup with a Map").
* **New problems (12):** `first-repeated-word` · `isomorphic-strings` · `word-pattern` · `ransom-note` · `jewels-and-stones` · `common-elements-k-arrays` · `happy-number` · `distinct-in-window` · `anagram-groups-sorted` · `longest-harmonious` · `pairs-with-difference-k` · `tag-set-ops` (union/intersection/difference output).
* Also: replace `group-anagrams-count` reuse in week 13 with review-marked slots (F-02).
* **Project:** `index.ts` inverted index — 8 tests.
* **Final:** Inverted index → 8 tests.
* **Quiz:** +34. **Cards:** 32.

### Week 10 — Unions, Aliases & Literal Types
*Now:* `ts_unions`, `ts_aliases`, `ts_enums` · final "Traffic light machine".

* **Chapters:** ✅ all three · ⬜ **`ts_literal_inference`** — widening rules, `as const`, readonly tuples from `as const`, deriving a union from an array (`typeof xs[number]`), `const` type parameters (preview).
* **Lesson additions:** union as "one of"; literal unions as the replacement for enums (erasable-syntax argument, D-5); `enum` graded by type-check only; union of objects vs object of unions; type aliases vs interfaces revisited.
* **Worked examples:** traffic light as a literal union + transition table; `const SIZES = ["S","M","L"] as const; type Size = typeof SIZES[number]`; the same thing as an enum, and why the union wins.
* **Pitfalls:** `let dir = "up"` widens to `string`; `enum` reverse mappings; numeric enums accept any number (older TS); `as const` on a mutable binding.
* **Exercises:** +8 drill, +4 predict, +4 diagnose (TS2322 string not assignable to literal union, TS2678), +2 fix, +2 design, **+3 type-graded**.
* **New problems (12):** `card-suit-rank` · `http-status-class` · `rps-tournament` · `vending-machine-states` · `door-lock-machine` · `compass-turns` · `size-converter` · `move-robot-grid` · `playlist-modes` (repeat/shuffle/off) · `unit-from-literal` · `weekday-type-parse` · `color-name-to-hex`.
* **Project:** `state.ts` — 10 tests incl. rejected transitions.
* **Final:** Traffic light machine → 8 tests.
* **Quiz:** +34. **Cards:** 36.

### Week 11 — Narrowing, Type Guards & Nullish *(D-2: `ts_nullish` moves here)*
*Now:* `ts_narrowing`, `ts_type_predicates` · 3 problems · final "Validate a batch of records".

* **Chapters:** ✅ `ts_narrowing`, `ts_type_predicates`, `ts_nullish` (moved) · ⬜ **`ts_control_flow`** — control-flow analysis in depth: assignments, early returns, `in`, `instanceof`, `Array.isArray`, **inferred type predicates** (TS 5.5: `xs.filter(x => x !== undefined)` narrows), **assertion functions** (`asserts x is T`), aliased conditions.
* **Lesson additions:** `typeof` guard table; truthiness narrowing and its `0`/`""` trap; `?.` and `??` and `??=`; `!` as an earned assertion vs a lie; narrowing does not survive callbacks; `unknown` → validated type as the core workflow; `noUncheckedIndexedAccess` on from here.
* **Worked examples:** validating a batch of JSON records with `isPerson(x: unknown): x is Person`; `assertIsDefined`; `filter` with an inferred predicate; a parser that returns `Person | null`.
* **Pitfalls:** a type predicate that lies (the compiler trusts it); narrowing lost after `await`/callback; `if (x)` excluding `0`; `!` hiding a real bug; `typeof null === "object"`.
* **Exercises:** +10 drill, +4 predict, +4 diagnose (TS18047, TS18048, TS2532, TS2339 on a union), +3 fix, +3 retype (`JSON.parse` → earned type), **+3 type-graded**.
* **New problems (12):** `parse-mixed-lines` · `sum-valid-numbers` · `validate-person-json` · `optional-chain-report` · `default-fill` · `safe-array-access-queries` · `first-defined` · `shape-area-guard` · `event-log-filter` · `nullable-average` · `deep-get-safe` · `coerce-or-reject`.
* **Project:** `validate.ts` — 10 tests, 5 of them failure paths.
* **Final:** Validate a batch of records → 8 tests.
* **Quiz:** +33. **Cards:** 44.

### Week 12 — Discriminated Unions
*Now:* `ts_discriminated_unions` · final "Stack language interpreter".

* **Chapters:** ✅ `ts_discriminated_unions` · ⬜ **`ts_top_bottom`** — `unknown`, `never`, `void`, `{}` vs `object` vs `Object`, exhaustiveness via `never`, `satisfies never`.
* **Lesson additions:** the tag field; `switch` on the tag; exhaustiveness as a refactoring tool (add a variant → the compiler lists every place to update); `Result<T, E>` as a discriminated union (preview of week 25); modelling states that carry data (`{ status: "done"; value } | { status: "failed"; error }`).
* **Worked examples:** shapes with area; an expression evaluator (`num | add | mul | neg`); a download state with per-state data; a reducer `(state, action) => state`.
* **Pitfalls:** tags that aren't literal types (`kind: string`); destructuring the tag loses narrowing (older TS) — show when it works now; optional tags; `default:` that swallows new variants.
* **Exercises:** +8 drill, +4 predict, +4 diagnose (TS2339 property on unnarrowed union, TS2322 in the `never` branch), +2 fix, +3 design, **+3 type-graded**.
* **New problems (14):** `shape-areas-union` · `expression-evaluator` · `calculator-rpn` · `todo-reducer` · `bank-events-replay` · `json-value-printer` (typed JSON union) · `traffic-events` · `vm-instructions` · `http-response-handler` · `undo-redo-actions` · `inventory-commands` · `chess-move-kinds` · `markdown-block-render` · `tokenizer-kinds`.
* **Project:** `interpreter.ts` — 10 tests; stretch: add `swap` and show the compiler pointing at every switch.
* **Final:** Stack language interpreter → 8 tests.
* **Quiz:** +33. **Cards:** 36.

### Week 13 — Tuples, Overloads & Function Types in Depth *(D-2)* + Checkpoint
*Now:* "Checkpoint — Consolidation", no chapters, contest "Months 1–3".

* **Chapters:** ⬜ **`ts_function_types`** — call signatures, construct signatures, `this` types, function type assignability (parameter bivariance preview), `ReturnType`/`Parameters` preview · ⬜ **`ts_type_testing`** — `Expect<Equal<A, B>>`, `@ts-expect-error`, how to *test* a type. Needed before months 4–5, which grade types.
* **Checkpoint (kept):** the 90-minute contest stays attached; quiz draws from weeks 9–12 via `quiz_from` (F-11).
* **Review:** 10 "review" problems from weeks 1–12 (explicitly `note: "review"`), interleaved.
* **Exercises:** +8 drill, +4 predict, +4 diagnose (TS2578 unused `@ts-expect-error`), **+6 type-graded** (write the assertion that fails for the wrong type).
* **New problems (8):** `typed-dispatcher` · `callback-registry` · `overloaded-parse` · `tuple-return-stats` · `variadic-sum` · `partial-apply-typed` · `event-handler-map` · `assert-types-kata` (type-graded).
* **Project:** re-implement the week 8 config reader from scratch, then add type tests for it.
* **Final:** Checkpoint: word frequency report → 8 tests.
* **Quiz:** 40, pulling from weeks 9–12. **Cards:** 28.

---

## Month 4 — Rigor (weeks 14–17)

**Month goal:** configure the compiler on purpose, understand why structural
typing is sometimes unsound, and make illegal values unconstructable.

**Month-level items**

| # | Item | P |
|---|---|---|
| M4-01 | **Type-graded problems (X-12) and two-part finals (X-34) live** before week 15. | **P0** |
| M4-02 | **tsconfig explorer** — an interactive tsconfig with every flag used in the programme; toggle one, see which of a fixed set of sample programs start or stop compiling. | P2 |
| M4-03 | **Multi-file project workspace** (X-45) — required for week 14's modules project. | P1 |
| M4-04 | **Month 4 checkpoint** (new): 90-minute contest + a 10-puzzle type-challenge section. | P1 |
| M4-05 | Arc project: **`ledger.ts` v4** — branded `Cents` and `AccountId`, a validated parser from untrusted JSON, `readonly` everywhere, derived types via utility types, split across modules. | P1 |

### Week 14 — The Toolchain: tsconfig, Modules & Declarations *(D-2)*
*Now:* "Nullability & Compiler Strictness" (`ts_nullish`, `ts_tsconfig`).

* **Chapters:** ✅ `ts_tsconfig`, `ts_modules`, `ts_declaration_files` (moved from 26) · ⬜ **`ts_erasable_syntax`** — type stripping, `--erasableSyntaxOnly`, `verbatimModuleSyntax`, `import type`/`export type`, why `enum`/`namespace`/parameter properties need a transform · ⬜ **`ts_versions`** — what changed in TypeScript 6.0 and what TypeScript 7 (native compiler) means for a project (D-4; author from the release notes).
* **Lesson additions:** what each `strict` sub-flag buys (`strictNullChecks`, `noImplicitAny`, `strictFunctionTypes`, `useUnknownInCatchVariables`…); `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noPropertyAccessFromIndexSignature`; `module`/`moduleResolution` (`nodenext`, `bundler`); ESM vs CJS; `.d.ts` files, `declare`, `declare global`, module augmentation; typing an untyped dependency.
* **Worked examples:** the same program under four tsconfigs; a `.d.ts` for a tiny untyped "library"; augmenting `Array` with a typed helper (and why you shouldn't); a two-module project in the multi-file workspace.
* **Pitfalls:** `import` of a type without `type` under `verbatimModuleSyntax`; default-export interop; circular imports; `skipLibCheck` hiding real errors; `any` leaking through a `.d.ts`.
* **Exercises:** +8 drill, +4 predict, +6 diagnose (flag-specific errors: TS2532, TS2375 exactOptional, TS4111 index-signature access, TS1484 type-only import), +2 fix, **+6 type-graded** (`.d.ts` authoring).
* **New problems (10):** `strict-lookup-table` · `safe-matrix-get` · `declare-a-library` (type-graded) · `augment-global-type` (type-graded) · `optional-vs-undefined` (exactOptional) · `module-barrel-api` (multi-file) · `config-merge-strict` · `env-var-parser` · `feature-flags-typed` · `cjs-vs-esm-quiz-kit` (predict-style).
* **Project:** multi-file `ledger/` — `types.ts`, `parse.ts`, `report.ts`, `main.ts`, plus a `money.d.ts`; 8 tests.
* **Final:** Safe lookup table → 8 tests under `strict+indexed`.
* **Quiz:** +34. **Cards:** 48.

### Week 15 — Assertions, `satisfies` & Structural Typing
*Now:* `ts_assertions`, `ts_satisfies`, `ts_structural_typing` · 2 problems · final "Route table with satisfies".

* **Chapters:** ✅ all three · ⬜ **`ts_variance`** — covariance, contravariance, method bivariance, array covariance unsoundness, `in`/`out` variance annotations.
* **Lesson additions:** `as` as a claim, not a conversion; double assertion `as unknown as T` and why it exists; `satisfies` keeps the literal type while checking; structural typing and "duck typing with a compiler"; excess-property checks only on fresh literals; unsoundness you can watch (the `Dog[]` → `Animal[]` push).
* **Worked examples:** route table with `satisfies Record<string, Route>` and a derived name union; the three-way comparison `: T` vs `as T` vs `satisfies T`; a callback parameter that accepts too much.
* **Pitfalls:** `as` silencing a real mismatch; `satisfies` with a union target; methods declared with method syntax are bivariant; a wider object keeps its extra keys at runtime.
* **Exercises:** +8 drill, +5 predict, +5 diagnose (TS2352 conversion may be a mistake, TS1360 satisfies failure, TS2561), +3 fix, **+6 type-graded**.
* **New problems (10, half type-graded):** `route-table-derive` · `theme-tokens-satisfies` · `icon-registry` · `palette-keys-union` (types) · `assignability-kata` (types) · `variance-kata` (types) · `mixed-shape-reader` · `plugin-registry` · `form-schema-satisfies` · `api-endpoints-map`.
* **Project:** `routes.ts` — 8 tests + 6 type assertions.
* **Final (two-part):** runtime route lookup (8 tests) + type half (route-name union assertions).
* **Quiz:** +30. **Cards:** 40.

### Week 16 — Branded Types & Immutability
*Now:* `ts_branded_types`, `ts_immutability` · 2 problems · final "Branded money".

* **Chapters:** ✅ both · ⬜ **`ts_parse_dont_validate`** — smart constructors, `unique symbol` brands, opaque types, making illegal values unconstructable.
* **Lesson additions:** `readonly` properties, `ReadonlyArray`, `Readonly<T>`, `as const`; shallow vs deep; `Object.freeze` two failure modes (silent in sloppy mode, throws in strict); aliasing bugs; structural sharing for cheap copies; `DeepReadonly` preview.
* **Worked examples:** `Cents`, `UserId`, `Email` brands with parsers; an immutable ledger with undo via history snapshots; `with()`/`toSorted()` for immutable updates.
* **Pitfalls:** `readonly` is compile-time only; a brand forged with `as`; `readonly` array passed to a function that mutates via a mutable alias; `Object.freeze` is shallow.
* **Exercises:** +8 drill, +4 predict, +4 diagnose (TS2540 read-only assignment, TS4104), +3 fix, +3 refactor ("make it immutable"), **+5 type-graded**.
* **New problems (10):** `money-arithmetic-branded` · `id-mixup-guard` (types) · `email-parse-smart` · `percent-bounds` · `immutable-cart-ops` · `undo-history-stack` · `persistent-list-ops` · `frozen-config-reader` · `deep-equal-immutable` · `time-travel-counter`.
* **Project:** `ids.ts` — 8 tests + type assertions that `UserId` ≠ `OrderId`.
* **Final (two-part):** Branded money.
* **Quiz:** +34. **Cards:** 36.

### Week 17 — Composition & Utility Types
*Now:* `ts_compose`, `ts_utility_types` · 3 problems (all interval problems) · final "Merge intervals".

* **Chapters:** ✅ both · ⬜ **`ts_runtime_validation`** — a mini schema library (`str()`, `num()`, `obj({...})`, `arr()`), `Infer<typeof schema>`, why validators and types must come from one source.
* **Lesson additions:** every built-in utility with a real use (`Partial`, `Required`, `Readonly`, `Pick`, `Omit`, `Record`, `Exclude`, `Extract`, `NonNullable`, `ReturnType`, `Parameters`, `Awaited`, `NoInfer`); the `Pick` constrained / `Omit` unconstrained asymmetry; `Omit` doesn't remove keys at runtime; composition over inheritance.
* **Worked examples:** `TaskDraft` / `TaskPatch` / `TaskSummary` derived from `Task`; an update function taking a `Partial`; a 60-line schema validator with inferred types.
* **Pitfalls:** `Omit<T, "typo">` compiles; `Partial` everywhere hides required data; spreading an `Omit` result leaks the omitted key.
* **Exercises:** +8 drill, +4 predict, +4 diagnose (TS2344), +3 fix, +3 design, **+6 type-graded**.
* **New problems (10):** `patch-apply` · `summary-projection` · `schema-validate-lines` · `record-totals` · `partial-merge-defaults` · `pick-omit-kata` (types) · `derive-from-model` (types) · `strip-secret-fields` (runtime `Omit`) · `typed-group-summary` · `form-errors-map`. Keep **one** interval problem as "applied"; move the other two to month 6's DS week.
* **Project:** `tasks.ts` + a schema validator; **arc:** `ledger.ts` v4 due.
* **Final (two-part):** replace "Merge intervals" with **"Typed patch API"** (runtime + types); move Merge intervals to a problem slot.
* **Quiz:** +34. **Cards:** 44.

---

## Month 5 — Generics & Type-Level Programming (weeks 18–22)

**Month goal:** write generic code whose types stay precise, and read and write
the type-level programs behind every serious library.

**Month-level items**

| # | Item | P |
|---|---|---|
| M5-01 | **Type evaluator** — paste a type, see it fully expanded, and **step** a conditional/mapped type's evaluation (distribution over each union member, each `infer` binding). The teaching tool for weeks 20–22. | P1 |
| M5-02 | **Type-challenge ladder** (X-24) surfaced as a daily rep: one puzzle a day, easy → extreme, streak tracked. | P1 |
| M5-03 | **Assertion panel** — for type-graded work, list every `Expect<Equal<…>>` with ✓/✗ and the two types side by side when it fails. | **P0** |
| M5-04 | **Month 5 checkpoint** (new): 20 type puzzles in 90 minutes + 2 runtime generic problems. | P1 |
| M5-05 | Arc project: **`typed-kit`** — a small library: `groupBy`, `pick`, `DeepReadonly`, `Paths<T>`, a typed event emitter, a route-param parser. Portfolio-grade. | P1 |

### Week 18 — Generics & Constraints
*Now:* `ts_generics`, `ts_generic_constraints` · 3 problems · final "Generic collection helpers".

* **Chapters:** ✅ both · ⬜ **`ts_generic_inference`** — how type arguments are inferred, `const` type parameters (TS 5.0), `NoInfer<T>` (TS 5.4), defaults, when to pass type arguments explicitly.
* **Lesson additions:** generic functions, interfaces, classes; `extends` constraints; `keyof` constraints; the "generic that should be a union" smell; too many type parameters; returning `T` vs returning `unknown`.
* **Worked examples:** `groupBy<T, K extends PropertyKey>`; `pluck<T, K extends keyof T>`; `first<T>(xs: readonly T[]): T | undefined`; `const` type parameter preserving literal tuples.
* **Pitfalls:** a type parameter used once (it's just `unknown`); `T extends object` accepting arrays; inference picking a wider type than intended; generic defaults that never apply.
* **Exercises:** +8 drill, +5 predict, +4 diagnose (TS2344, TS2322 "T could be instantiated with an arbitrary type"), +3 fix, +3 design, **+8 type-graded**.
* **New problems (12):** `generic-group-by` · `generic-partition` · `generic-unique-by` · `generic-zip` · `generic-chunk` · `typed-pluck` · `min-by-max-by` · `generic-lru` (runtime) · `typed-memo` · `generic-stack` · `infer-literal-tuple` (types) · `constraint-kata` (types). Plus `kth-largest-element` retained as applied.
* **Project:** `collections.ts` — 10 tests + type assertions.
* **Final (two-part):** Generic collection helpers.
* **Quiz:** +33. **Cards:** 40.

### Week 19 — `keyof`, `typeof` & Indexed Access
*Now:* `ts_keyof_indexed` · 2 problems · final "Settings from one source of truth".

* **Chapters:** ✅ `ts_keyof_indexed` · ⬜ **`ts_lookup_types`** — `T[K]`, `T[number]`, `T["a" | "b"]`, tuple element access, `typeof obj[keyof typeof obj]`, `PropertyKey`.
* **Lesson additions:** type-level `typeof` vs runtime `typeof`; `keyof` of a union vs intersection; deriving everything from one `as const` object; `Object.keys` doesn't return `keyof T` (and why that's correct).
* **Worked examples:** settings getters/setters derived from defaults; typed `get(obj, key)`; a `Values<T>` helper; a column list whose type drives a table printer.
* **Pitfalls:** `keyof` including `number` for index signatures; `keyof {}` is `never`; a typed `Object.keys` cast that lies.
* **Exercises:** +6 drill, +6 predict, +4 diagnose (TS2536, TS7053), +2 fix, **+10 type-graded**.
* **New problems (10):** `typed-get-set` · `settings-derive` · `column-printer-typed` · `enum-like-object` · `values-of` (types) · `keys-of-type-value` (types) · `tuple-to-union` (types) · `event-payload-lookup` · `i18n-keys-typed` · `lookup-table-report`.
* **Project:** `settings.ts` — 8 tests + assertions ("adding a setting is one line").
* **Final (two-part):** Settings from one source of truth.
* **Quiz:** +34. **Cards:** 32.

### Week 20 — Mapped Types
*Now:* `ts_mapped_types` · 2 problems · final with **2 tests** (F-04).

* **Chapters:** ✅ `ts_mapped_types` · ⬜ **`ts_key_remapping`** — `as` clauses, filtering keys to `never`, template-literal key names (`getX`), homomorphic mapped types preserving modifiers.
* **Lesson additions:** `{ [K in keyof T]: … }`; `+readonly`/`-readonly`, `+?`/`-?`; rebuilding `Partial`/`Required`/`Readonly`/`Pick`/`Record` by hand; mapping over unions vs over object keys; `DeepPartial`/`DeepReadonly`.
* **Worked examples:** `Getters<T>` producing `getName(): string`; `PickByValue<T, V>`; `Mutable<T>`; `Nullable<T>`.
* **Pitfalls:** mapped type over a primitive; losing optionality by mapping over `keyof T` indirectly; `DeepReadonly` on functions and `Date`.
* **Exercises:** +4 drill, +6 predict, +3 diagnose, **+14 type-graded**.
* **New problems (10, mostly type-graded):** `my-partial` · `my-readonly` · `my-pick` · `my-record` · `getters-type` · `pick-by-value` · `omit-by-value` · `mutable` · `deep-readonly` · `form-state-from-model` (runtime + types).
* **Project:** `utils.d.ts` — reimplement five built-ins with type tests (already the brief; now judged).
* **Final:** → 8 tests + 10 assertions.
* **Quiz:** +34. **Cards:** 32.

### Week 21 — Conditional Types & `infer`
*Now:* `ts_conditional_types` · 2 unrelated DSA problems (F-03).

* **Chapters:** ✅ `ts_conditional_types` · ⬜ **`ts_distributive`** — distribution over naked type parameters, `[T] extends [U]` to stop it, `never` as the empty union, `infer U extends X` constraints.
* **Lesson additions:** `T extends U ? X : Y`; `infer` in function, array, promise and template positions; rebuilding `ReturnType`, `Parameters`, `Awaited`, `Exclude`, `Extract`, `NonNullable`; `IsNever`, `IsAny`, `IsUnion` tricks; conditional types in function return positions and why implementations need assertions.
* **Worked examples:** `ElementOf<T>`; `UnwrapPromise<T>` recursively; `FunctionArgs<F>`; `IsEqual<A, B>` and why the naive version fails.
* **Pitfalls:** unexpected distribution; `any` distributing to both branches; `never` input returning `never`; return-type conditional forcing a cast.
* **Exercises:** +4 drill, +6 predict, +3 diagnose, **+15 type-graded**.
* **New problems (12, type-graded):** `my-return-type` · `my-parameters` · `my-awaited` · `my-exclude` · `element-of` · `is-never` · `is-union` · `last-of-tuple` · `first-of-tuple` · `flatten-tuple` · `function-first-arg` · `unwrap-result`. Keep one runtime problem: `compact-and-unwrap` (the current final's idea).
* **Project:** `types.ts` — the brief, now judged.
* **Final (two-part):** Unwrap and compact.
* **Quiz:** +34. **Cards:** 32.

### Week 22 — Template Literals & Recursive Types
*Now:* `ts_template_literal_types`, `ts_type_level` · 2 problems.

* **Chapters:** ✅ both · ⬜ **`ts_type_performance`** — recursion depth limits, tail-recursive conditional types, instantiation cost, "type instantiation is excessively deep" (TS2589), when to stop.
* **Lesson additions:** `` `${A}-${B}` ``; `Uppercase`/`Lowercase`/`Capitalize`/`Uncapitalize`; parsing strings at the type level (`Split`, `Trim`, route params); recursive types (`Json`, trees, `Paths<T>`); tuple manipulation (`Reverse`, `Length`, `Push`); type-level arithmetic via tuples (and why it's a toy).
* **Worked examples:** `RouteParams<"/users/:id/posts/:postId">`; `Paths<T>` for typed `get("a.b.c")`; typed event names `${Entity}:${Action}`; `CamelCase<"foo_bar_baz">`.
* **Pitfalls:** unions in template literals exploding (cartesian product); TS2589 depth errors; recursion on `string` (not a literal) returning `string`.
* **Exercises:** +4 drill, +6 predict, +3 diagnose (TS2589), **+15 type-graded**.
* **New problems (12, type-graded + 2 runtime):** `route-params` · `split-string-type` · `trim-type` · `camel-case-type` · `kebab-case-type` · `paths-of` · `get-by-path` (runtime + types) · `tuple-reverse` · `tuple-length` · `json-type` · `event-name-union` · `typed-emitter` (runtime + types). Keep `implement-trie-ops` as applied.
* **Project:** `events.ts` typed emitter; **arc:** `typed-kit` due.
* **Final (two-part):** Event catalogue.
* **Quiz:** +33. **Cards:** 36.

---

## Month 6 — Runtime & Architecture (weeks 23–26, + optional 27)

**Month goal:** build real programs — classes with invariants, lazy pipelines,
error handling that can't be forgotten, and async code that is correct under
concurrency and cancellation.

**Month-level items**

| # | Item | P |
|---|---|---|
| M6-01 | **Event-loop visualiser** — for a snippet with `setTimeout`, `Promise.then`, `queueMicrotask` and `await`, animate call stack / microtask queue / task queue and the resulting print order. Teaching tool for week 26. | P1 |
| M6-02 | **Async timeline** — for `Promise.all`/`allSettled`/`race`/`any` over simulated delays, draw each promise's lifetime and when the combinator settles. | P2 |
| M6-03 | **Deterministic async rule** (as the course's `java_m30_sync.py` header): output must be deterministic *by construction* — simulated clocks, index-ordered printing, never timing-dependent. Build lint for `setTimeout` with non-constant delays. | **P0** |
| M6-04 | **Class diagram** — render a class hierarchy (fields, visibility, `implements`/`extends`) from the learner's code. | P3 |
| M6-05 | **Month 6 checkpoint** = the existing week-26 contest, rebuilt from month 6 problems. | P1 |
| M6-06 | Arc project: **`ledger` final** — classes with private state, a generator-based report stream, `Result`-based parsing, an async loader with timeout and cancellation. | P1 |

### Week 23 — Classes & Encapsulation
*Now:* `ts_classes`, `ts_this_accessors` · 3 problems · final "Bank account with invariants".

* **Chapters:** ✅ both · ⬜ **`ts_class_design`** — `abstract` classes, `implements`, `override`, `protected`, mixins, composition vs inheritance, `static` factories, class vs closure-based objects · ⬜ **`ts_decorators`** — TC39 standard decorators and `accessor` (type-graded only — D-5).
* **Lesson additions:** `#private` vs `private`; parameter properties (type-graded only); getters/setters with validation; `this` binding and arrow-method fields; `instanceof` narrowing; classes are also types (structural!).
* **Worked examples:** `BankAccount` with a `#balance` invariant; `Shape` abstract class vs a discriminated union — same problem, both designs; a `static from()` factory with validation.
* **Pitfalls:** detached method losing `this`; `private` is compile-time only (`#` is real); two classes with the same shape are interchangeable; a setter assigning to itself (infinite recursion).
* **Exercises:** +8 drill, +4 predict, +5 diagnose (TS2341 private access, TS2415, TS4114 missing `override`, TS2511 abstract instantiation), +4 fix, +2 design, **+3 type-graded** (parameter properties, decorators).
* **New problems (12):** `bank-account-class` · `temperature-class-accessors` · `rate-limiter-class` · `matrix-class-ops` · `vector2d-immutable` · `shape-hierarchy` · `parking-lot-oop` · `library-checkout` · `elevator-sim-steps` · `inventory-class` · `observable-value` · `state-machine-class`. Plus `design-circular-queue`, `design-linked-list`, `lru-cache` retained.
* **Project:** `account.ts` — 10 tests incl. overdraft rejections.
* **Final:** Bank account with invariants → 8 tests.
* **Quiz:** +34. **Cards:** 40.

### Week 24 — Iterators, Generators & Generic Data Structures
*Now:* `ts_iterators`, `ts_ds_generics` · final "Lazy pipeline over an infinite source".

* **Chapters:** ✅ both · ⬜ **`ts_iterator_helpers`** — ES2025 iterator helpers (`Iterator.prototype.map/filter/take/drop/flatMap/reduce/toArray`, `Iterator.from`), `Symbol.iterator` on your own classes · ⬜ **`ts_heap_pq`** — a generic binary heap / priority queue with a comparator (the DS the course arc needs for heaps).
* **Lesson additions:** the iterator protocol; generators (`function*`, `yield`, `yield*`, `return`); `Generator<T, TReturn, TNext>`; laziness and infinite sequences; typed generic `Stack<T>`, `Queue<T>` (and the O(n) `shift` trap), `LinkedList<T>`, `BinaryTree<T>`, `Heap<T>`.
* **Worked examples:** `range`, `take`, `chunk` generators; an iterable `LinkedList<T>` usable in `for…of` and spread; a `PriorityQueue<T>` driving "k smallest"; an in-order tree iterator via `yield*`.
* **Pitfalls:** a generator is single-use; spreading an infinite iterator hangs; `shift()` in a BFS loop is O(n); comparator sign mistakes.
* **Exercises:** +8 drill, +4 predict, +3 diagnose, +3 fix, +3 design, **+3 type-graded**.
* **New problems (14):** `lazy-primes` · `take-while-gen` · `interleave-iterators` · `iterable-linked-list` · `tree-inorder-iterator` · `bst-iterator` · `generic-min-heap` · `k-smallest-heap` · `merge-k-sorted-heap` · `ring-buffer` · `deque-generic` · `task-scheduler-pq` · `running-median-heaps` · `meeting-rooms-heap`. Plus the two interval problems moved from week 17.
* **Project:** `lazy.ts` — 8 tests.
* **Final:** Lazy pipeline over an infinite source → 8 tests.
* **Quiz:** +31. **Cards:** 44.

### Week 25 — Errors, `Result` & Resource Management *(D-2)*
*Now:* "Errors & Async" with four chapters.

* **Chapters:** ✅ `ts_errors`, `ts_error_types` · ⬜ **`ts_resource_management`** — `using` / `await using`, `Symbol.dispose`, `DisposableStack` (runs on the installed Node 24) · ⬜ **`ts_error_cause`** — `Error` subclasses, `cause`, `AggregateError`, `useUnknownInCatchVariables`, typed error unions.
* **Lesson additions:** `catch (e: unknown)` and narrowing it; custom error classes; `Result<T, E>` as a discriminated union; when to throw vs return; error boundaries at the edge of a program; cleanup with `finally` vs `using`.
* **Worked examples:** a `Result`-returning parser chain with `map`/`andThen`; `ValidationError` with `cause`; a file-like resource closed deterministically with `using` (printing "opened"/"closed"); collecting all errors vs failing fast.
* **Pitfalls:** throwing strings; `e.message` on `unknown`; swallowed errors in `catch {}`; `finally` overriding a `return`; a `Result` that's ignored.
* **Exercises:** +8 drill, +4 predict, +4 diagnose (TS18046 `e` is unknown), +3 fix, +3 retype, **+3 type-graded**.
* **New problems (12):** `result-parse-chain` · `collect-all-errors` · `error-cause-chain-print` · `retry-with-result` · `safe-json-parse` · `validate-and-report` · `using-resource-order` · `disposable-stack-order` · `aggregate-validation` · `error-class-hierarchy` · `fail-fast-vs-collect` · `exception-to-result`.
* **Project:** `parse.ts` — a `Result`-based CSV parser with line-numbered errors; 10 tests.
* **Final:** new **"Result-based config loader"** → 8 tests.
* **Quiz:** +34. **Cards:** 40.

### Week 26 — Async, Concurrency & Cancellation *(D-2)*
*Now:* "Modules, Declarations & Capstone".

* **Chapters:** ✅ `ts_async`, `ts_async_patterns` (moved from 25) · ⬜ **`ts_event_loop`** — call stack, microtasks vs tasks, `await` ordering, `queueMicrotask` · ⬜ **`ts_cancellation`** — `AbortController`, `AbortSignal.timeout`, `AbortSignal.any`, `Promise.withResolvers`, `Promise.try` · ⬜ **`ts_async_iteration`** — `for await`, async generators, `Array.fromAsync`.
* **Lesson additions:** promises and states; `async`/`await` sugar; sequential vs concurrent; `Promise.all` / `allSettled` / `race` / `any` and their typed results; concurrency limits (a pool); timeouts; `Awaited<T>`; unhandled rejections.
* **Worked examples:** load 5 simulated resources with concurrency 2, printing in index order; race each against a timeout and return a `Result` per resource; a cancellable retry loop; an async generator paginating a simulated API.
* **Pitfalls:** `forEach` with an async callback; `await` in a loop when you meant concurrency; `Promise.all` failing fast and losing other results; forgetting to `await` (TS floating promise); output depending on timing (M6-03).
* **Exercises:** +8 drill, +6 predict (print-order questions), +3 diagnose (TS2801, TS1308), +4 fix, +3 order (Parsons for event-loop ordering).
* **New problems (12):** `event-loop-order` · `sequential-vs-parallel-sum` · `promise-pool-limit` · `all-settled-report` · `race-timeout-result` · `retry-exponential-sim` · `async-pagination-gen` · `cancellable-task` · `debounce-sim-clock` · `throttle-sim-clock` · `async-queue-fifo` · `dependency-loader-topo`. Plus `hit-counter`, `stock-spanner`, `median-from-stream` retained.
* **Project:** `fetchAll.ts` — 10 tests (the current week-25 brief, now judged).
* **Final:** Concurrent loads with a `Result` → 8 tests.
* **Quiz:** +34. **Cards:** 44.
* **Checkpoint:** month-6 contest (M6-05).

### Week 27 — Capstone & Mock Interview *(optional, ungated — D-2)*

* **Capstone:** the multi-file typed CLI from today's week-26 brief — `Result` parser, branded ids, generic store with an iterator, a `.d.ts` for a pretend dependency, async loader — with 20 acceptance tests and a rubric.
* **Mock interview kit:** 3 timed 45-minute sessions, each one TS-idiom question set + one DSA problem in TS + one type-level puzzle; self-scored rubric (communication, correctness, types, tests).
* **TypeScript interview bank:** 60 conceptual questions with model answers (`any` vs `unknown` vs `never`; `interface` vs `type`; structural typing; variance; `satisfies`; declaration merging; erasable syntax; how would you type `pipe`; etc.).
* **Code-review exercises:** 10 PR-sized snippets — find the typing problems, write the review comments, compare to the model review.
* **Completion summary** (X-68) and certificate-style page.

---

## Totals — what "done" looks like

| | now | target |
|---|---|---|
| TypeScript Learn chapters | 50 | **87** (37 new) |
| Lesson length | 0.9–2.1k chars | 4–8k chars, templated |
| Learn exercises on those chapters | 176 (2 kinds) | **~1,300** (10+ kinds, ~20% type-graded) |
| Curated problems | 85 slots, 26 TS-startable | **~380 slots, all TS-startable** (~300 new originals, ~100 of them type-graded) |
| Type-challenge bank | 0 | **~120** |
| Quiz bank | 170 | **~1,050**, 10 sampled |
| Flashcards | 0 | **~1,000** |
| Final tests | 94 (2–5/week) | **~200** (≥ 6 per final, most 8) + hidden sets, + 26 alternates |
| Checkpoints | 2 | 6 monthly + final exam |
| Projects | 26 ungraded sentences | 26 structured, runnable, tested + 1 arc project across 6 months |

---

## Suggested batching

Every batch ends green and committable.

| Batch | Contents | Why first |
|---|---|---|
| **A** | F-01 TS starters, F-02 dupes, F-04 final tests, X-100 build asserts, X-101 Mastery verifier | Fixes the track as it stands; everything after depends on the verifier |
| **B** | X-12 type-graded problems, X-23 TS function harness, X-10/X-11 exercise kinds, M5-03 assertion panel | The machinery months 2, 4 and 5 need |
| **C** | X-62 hovers, X-63 squiggles, X-66 error glossary, M1-02 I/O visualiser, X-70 quiz review | The UI that makes month 1 teach |
| **D** | D-2 rebalance, X-01 file split | Structural; do before bulk authoring |
| **E** | Month 1 content | Lowest risk, highest traffic |
| **F** | Month 2 content + X-44 arc project | Needs the TS harness (B) |
| **G** | Month 3 content + M3-01 narrowing stepper | |
| **H** | Month 5 content + X-24 type-challenge bank | Graded entirely by types — like the course's weeks 29–31, the lowest-risk advanced content; can run in parallel with G |
| **I** | Month 4 content + X-45 multi-file workspace | |
| **J** | Month 6 content + M6-01 event-loop visualiser + week 27 | Highest runtime risk (async determinism) |
| **K** | X-30/X-50 bank and card top-ups, X-35 checkpoints, X-36 final exam, X-68 summary | Assessment polish across everything |

---

## Constraints every week must satisfy

* **Erasable syntax only, unless type-graded** (D-5). `enum`, `namespace`,
  parameter properties and decorators never run.
* **Quote only errors the compiler really emits.** Every `diagnose` prompt and
  every `errors`/pitfall code is re-derived from its starter (X-103). The code
  depends on the syntactic form — see the TS2353/TS2561, TS18048/TS2532,
  TS2741/TS2345 table in `TS_ROADMAP.md`.
* **Nothing before its week** (X-104). A week-5 problem may not need week-18
  generics to be solved idiomatically.
* **Deterministic async** (M6-03). Timing never decides output.
* **Expected output is computed, not typed** — every test's expected output
  comes from running the reference solution, as everywhere else in the app.
* **Original problems only.** No copied problem statements.
* **Every chapter scheduled exactly once**; the build asserts it.
* **Both runtime and type verifiers pass** before a batch is committed.
