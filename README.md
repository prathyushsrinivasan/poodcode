# Poodcode

A personal, **offline-first** coding-interview & algorithm-practice desktop app.
Not a LeetCode clone or a public product — a private tool for learning, spaced
repetition, and interview prep. No accounts, no cloud, no telemetry. Your
problems, code, notes, and stats live in a local SQLite database.

Built with **Tauri 2 · React + TypeScript · Rust · SQLite · Monaco · ECharts**.

---

## Quick start

Prerequisites (already verified on this machine):

- **Node.js** 18+ (22+ recommended — enables running TypeScript solutions)
- **Rust** toolchain (`cargo`, `rustc`) with the MSVC build tools on Windows
- For running solutions in a language: that language's toolchain on `PATH`
  (Python, Java/JDK, Node, Rust work out of the box here; C++/Go/C#/Kotlin
  light up automatically once installed).

```bash
npm install          # one-time: install frontend deps
npm run app          # launch the desktop app (tauri dev)
```

To produce a distributable build (standalone exe + installer):

```bash
npm run app:build
```

### Tests

```bash
npm test                       # frontend logic (Vitest): revision, filters, complexity
cd src-tauri && cargo test     # backend: scheduler + live execution/judging pipeline
python tools/verify_backend.py --starters       # Backend Lab: every solution passes, every starter fails
python tools/verify_java_course.py --starters   # Java course: same, via javac/java (needs a JDK)
python tools/verify_projects.py --starters      # Projects: same, type-checked then run via Node
```

The first launch seeds **29 original problems** — 8 below-Easy **Intro** problems
for someone new to Java, plus 21 across arrays, strings, hashing, sliding window,
stacks, binary search, graphs, and dynamic programming — and a **Learn** library
of **37 concept lessons**. **Java is the default language**, and every problem
ships with a tailored Java starter.

---

## Architecture

Clean separation across four layers; everything is modular and offline.

```
Poodcode/
├─ src/                        # ── UI layer (React + TypeScript)
│  ├─ pages/                   # Dashboard, Library, Solve, Statistics, Revision,
│  │                          #   Timeline, RandomPractice, Companies, Interview,
│  │                          #   Settings, ProblemForm
│  ├─ components/              # Editor, Markdown, TestResults, TestCaseManager,
│  │                          #   Charts, CommandPalette, common widgets
│  ├─ lib/                     # ── Pure business logic (unit-tested, framework-free)
│  │  ├─ revision.ts           #   spaced-repetition ladder (mirrors Rust)
│  │  ├─ filters.ts            #   library filtering + sorting
│  │  ├─ complexity.ts         #   heuristic Big-O analyzer + comparison
│  │  ├─ templates.ts          #   per-language stdin skeletons
│  │  └─ format.ts             #   duration/date formatting
│  ├─ api.ts                   # typed wrappers over Tauri commands (the UI↔core seam)
│  ├─ store.ts                 # app state + preferences (zustand)
│  └─ types.ts                 # shared data models (mirror Rust serde structs)
│
├─ src-tauri/                  # ── Rust backend
│  ├─ src/
│  │  ├─ db.rs                 # ── Database layer: schema, migrations, connection
│  │  ├─ models.rs             #   serde data models
│  │  ├─ repo.rs               # ── Business logic: repositories, progress, scheduler
│  │  ├─ stats.rs              #   statistics aggregation (streaks, heatmap, mastery)
│  │  ├─ exec.rs               # ── Code execution: pluggable per-language runners
│  │  ├─ judge.rs              #   compile-once, run-per-case judging + normalization
│  │  ├─ commands.rs           # Tauri command surface (the only IPC entry points)
│  │  ├─ error.rs              # unified error type
│  │  ├─ lib.rs                # app setup, DB open + seed, command registration
│  │  └─ tests.rs              # backend logic unit tests
│  ├─ tests/exec_judge.rs      # execution/judging integration tests (real toolchains)
│  ├─ tests/verify_backend_course.rs  # proves every Backend Lab solution passes
│  ├─ tests/verify_java_course.rs     # proves every Java course solution passes
│  ├─ seeds/problems.json      # the bundled original problem set
│  ├─ seeds/backend_course.json       # Backend Lab: 7 CRUD-API build projects
│  ├─ seeds/java_course.json          # Java course: 31 modules past the basics
│  └─ seeds/projects.json             # Projects: the Todo API, 20 TS modules
│
├─ tools/gen_seed.py           # generator that AUTHORS every seeds/*.json
├─ tools/backend_course.py     # authors seeds/backend_course.json
├─ tools/java_course.py        # authors seeds/java_course.json (+ java_m01…m31, java_p01…p31)
├─ tools/projects_track.py     # authors seeds/projects.json (+ todo_m01…m20)
├─ tools/verify_backend.py     # fast Node loop: runs every Backend Lab solution
├─ tools/verify_java_course.py # fast javac/java loop: runs every Java solution
└─ tools/verify_projects.py    # fast tsc+Node loop: runs every Projects solution
```

The **UI never touches the database or the filesystem directly** — it goes
through `api.ts` → Tauri commands → repositories. The **execution engine** is
fully decoupled from problem content and judging, so adding a language or a
problem never touches unrelated code.

---

## How code execution works

Programs communicate over **stdin/stdout**. A test case is an `input` (fed to
stdin) and an `expected_output` (compared to stdout). This model is completely
language-agnostic — the same problem judges identically in any language.

- Output is compared after **normalization** (trailing whitespace on each line
  and trailing blank lines are ignored), so cosmetically-different-but-correct
  output still passes.
- Each run is **sandboxed to a temp directory**, has a **wall-clock timeout**
  (6 s), and reader threads drain stdout/stderr to avoid pipe deadlocks.
- Compiled languages (Java, Rust, C++, Go) **compile once**, then reuse the
  artifact across every test case.
- **Run** uses your example/custom cases (or a scratch stdin box); **Submit**
  runs the hidden cases, records an attempt, updates progress, and schedules a
  review.

| Language   | How it runs                        | Status here      |
|------------|------------------------------------|------------------|
| Python     | `python -u main.py`                | ✅ installed     |
| JavaScript | `node main.js`                     | ✅ installed     |
| TypeScript | `node main.ts` (native type-strip) | ✅ installed     |
| Java       | `javac` → `java Main`              | ✅ installed     |
| Rust       | `rustc -O` → run binary            | ✅ installed     |
| C++        | `g++ -O2` → run binary             | ○ plug-in        |
| Go         | `go build` → run binary            | ○ plug-in        |
| C#         | `dotnet`                           | ○ plug-in        |
| Kotlin     | `kotlinc`                          | ○ plug-in        |

Not-installed languages appear in the picker with an install hint and activate
automatically once their toolchain is on `PATH` (restart to re-detect).

---

## Problem content

All bundled problems are **original to this app** (statements, tests,
editorials, hints) — no third-party/proprietary problems are copied.

Test-case correctness is guaranteed by construction: `tools/gen_seed.py` holds a
**reference solution** for every problem and *computes* each expected output, so
hidden tests can't drift from the intended behavior. Regenerate with:

```bash
python tools/gen_seed.py       # writes every src-tauri/seeds/*.json
```

### Backend Lab

A **project-based** track (`seeds/backend_course.json`, authored in
`tools/backend_course.py`) that builds a CRUD HTTP API from nothing, in **seven
projects**: a bare `node:http` server → CRUD on a resource → validation and
error contracts → persistence on disk → search/filter/sort/paginate →
users, tokens and ownership → routers, middleware, an error boundary and a
test runner. Each project reopens the previous one's code, so it is a build
ladder rather than a reading list.

Every project ships the same four things: **instructions** (what to do, in
order), a **checkpoint** per step (the observable result that proves it worked),
judged **drills / fix-the-bug programs / a final build**, and an **acceptance
checklist** plus **curl commands** to test the copy running on your own machine.

Two constraints shaped the content. It uses **Node built-ins only** — no
Express, no `npm install`, matching the offline-first design and making the
"what is a framework actually doing" question answerable. And every judged
exercise **boots a real server on port 0** and replays a request script read
from stdin (`METHOD /path [@token] [json body]` → `<status> <body>`), so a
routing mistake shows up as a wrong status code rather than a mystery.

Correctness is proved twice: `tools/verify_backend.py` runs every reference
solution through Node in a fast authoring loop, and
`src-tauri/tests/verify_backend_course.rs` runs the same programs through the
**real judge the app uses** — and both also assert that each starter *fails*, so
no blank is decorative.

### Projects

A **build ladder** (`seeds/projects.json`, authored in `tools/projects_track.py`
plus one file per module) that takes one real application and breaks it down as
far as it will go. The first — and, for now, only — project is a **Todo API**:
a complete, validated, persistent CRUD service over plain `node:http`, in
**TypeScript**, with no dependencies at all. **Twenty modules in five phases:**
model the data → put it on the network → full CRUD → make it trustworthy →
make it real. **Modules 1-4 ship today: 16 steps and 29 judged exercises.**

Where the Backend Lab's unit is a *project* you finish in an evening, this
track's unit is a **module** — one 30-60 minute slice that adds exactly one
capability and answers five questions in order:

1. **Why does this module exist?** — the problem the previous one left behind.
2. **Where does it sit?** — its phase on the roadmap, and what the app can do at
   the end of it that it could not at the start.
3. **What syntax do I need?** — every piece of TypeScript the module uses, with
   its meaning, a worked example and the mistake people make, taught *before* it
   is used.
4. **What do I do?** — ordered steps, each with a checkpoint that tells you
   whether it worked, plus the pitfalls that cost people an hour.
5. **Did I get it?** — judged exercises you write yourself, an acceptance
   checklist, and a **revealable reference implementation** for the whole module.

The headline claim is that you are never asked to write a line of TypeScript the
track has not already put in front of you, and it is **enforced at build time
rather than promised in prose**. Two gen-time lints read one table: `_lint_scope`
fails the build if a module uses a token a later module introduces, and
`_lint_syntax_taught` fails it unless the introducing module also *teaches* that
token in its syntax primer. (It works — module 2's demo reached for `.splice(`,
which module 12 owns, and the build refused.)

Everything runs under the same judge as the rest of the app, type-checked at
`strict` plus `noUncheckedIndexedAccess` before it runs — which is content, not
ceremony: module 10 reads segment 2 of a URL path, and `/todos` has no segment 2.
Server programs boot a real `node:http` server on port 0 and replay a request
script from stdin, so a routing bug shows up as a wrong status code. Correctness
is proved twice, by `tools/verify_projects.py` and
`src-tauri/tests/verify_projects.rs`, which also assert that every starter
*fails*.

The plan for the remaining 17 modules, and the six decisions taken before
authoring, live in [`PROJECTS_ROADMAP.md`](PROJECTS_ROADMAP.md).

### TypeScript course

The one track that starts at **zero** (`seeds/ts_course.json`, authored in
`tools/typescript_course.py`): *TypeScript: Zero to Interview*, an eight-month,
**32-week** course from a first `console.log` to interview-ready — DSA solved in
TypeScript plus deep type-system work. **Weeks 1-15 ship today: 119 lessons and
882 judged exercises**, each week carrying a goal, warm-ups, drills,
fix-the-bug programs, a coding challenge, hint ladders, a glossary, a cheat
sheet, a self-check, a review quiz and an instalment of a **capstone project
that grows across the whole course** (Budget Buddy, from a receipt line in week
1 to a generic record toolkit in week 10, a class-owned ledger in week 11, a
branded `Money` type in week 12, an immutable ledger with undo in week 13, a
derived patch API in week 14 and a validating JSON loader in week 15).

Beyond the usual drill/fix/challenge, the course grades **reading** as well as
writing, with four kinds aimed at what using TypeScript actually feels like:
*predict the type* the compiler infers, *read the error* and repair its cause,
*retype the `any`* until the types say something, and *design the type first*.
Two of these need no runtime at all — a type has no output to compare, so
they're graded on the type-check alone (`judge_mode: "types"`), with hidden
`Expect<Equal<…>>` assertions.

Four constraints shape it. **Nothing before its week** — a gen-time linter
fails the build if a program uses an idea a later week teaches. **The compiler
tightens as you go**: every program is type-checked before it runs, and from
week 6 under `noUncheckedIndexedAccess`, so `a[i]` is `T | undefined` and has to
be handled. A *read-the-error* exercise must quote an error the compiler
**really emits** — the verifier re-derives the `TSnnnn` code from the starter
and fails if the quoted one is invented. And programs must be **erasable
syntax**: the judge strips types rather than compiling them, so the three
constructs that emit code — parameter properties (week 11), `enum` (week 12)
and `namespace` — are taught as type-checked exercises instead, which is itself
one of the reasons week 12 argues for a literal union over an enum.

The plan for the remaining 17 weeks — including the five decisions worth taking
before authoring resumes — lives in [`TS_ROADMAP.md`](TS_ROADMAP.md).

### Java course

A **topic-based** track (`seeds/java_course.json`, authored in
`tools/java_course.py` plus one file per module) for someone who already has
Java's basics — variables, `if`/`else`, loops, printing — and stalls at the
point where syntax knowledge has to turn into fluency. Twenty-eight modules:

- **Arrays**, in depth — memory model, grids, sorting and searching by hand,
  rotation and counting, prefix sums / two pointers / sliding window
- **Strings** — the immutable object behind the text, the API and the classic
  problems, `StringBuilder`
- **Methods** — signatures, pass-by-value, overloading, scope, varargs, recursion
- **Object-oriented programming** — classes and objects, encapsulation and
  invariants, inheritance, polymorphism and the `equals`/`hashCode` contract,
  then abstraction: abstract classes, interfaces, `default` and `static`
  interface methods, `final`, and the argument for composition over inheritance
- **Exception handling** — what an exception is and how to read a stack trace,
  `try`/`catch`/`finally`, the hierarchy and multi-catch, then `throw`,
  checked vs unchecked, custom exception types and try-with-resources
- **The collections framework** — `List` and the boxing traps that come with
  it, `Set` and `Map` in their hashed, insertion-ordered and sorted flavours,
  queues, deques, stacks and heaps, then `Comparable`, `Comparator`, sorting,
  and choosing a collection by cost

- **Generics** — why they exist, writing `class Box<T>` and `Pair<A, B>`,
  generic methods and bounded type parameters, wildcards (invariance,
  `? extends`, `? super` and PECS), and finally erasure: what the compiler
  actually emits, why `new T()` and `static T` are illegal, where an unchecked
  cast's `ClassCastException` really lands, bridge methods, and `Class<T>`
  type tokens

- **Java 8+** — lambdas and the four `java.util.function` shapes, writing your
  own functional interface, capture and effectively-final, closures, the four
  kinds of method reference; stream pipelines — laziness, single-use,
  `filter`/`map`/`sorted`/`distinct`/`limit`/`skip`, and the terminal that
  actually runs the work; then `collect`, `groupingBy` and its downstream
  collectors, `partitioningBy`, `toMap`'s duplicate-key trap, `reduce` and its
  identity, and the primitive streams that avoid boxing; and finally
  `Optional` — `orElse` vs `orElseGet`, `map`/`filter`/`flatMap`, the stream
  terminals that return one, and the three places it makes code worse

- **Multithreading** — processes vs threads and what they share; `Runnable`,
  `start()` vs `run()`, the six lifecycle states, and `join()` as both a wait
  and a *publish*; interruption as a request, and daemon threads; then shared
  state — the lost update, `synchronized` and which object it locks, why
  `volatile` gives visibility and never atomicity, atomics and
  compare-and-set, `ReentrantLock`, and deadlock cured by lock ordering; and
  finally executors — `Callable` and `Future`, where a failed task's exception
  goes, collecting results in submission order with `invokeAll`, the forgotten
  `shutdown()` that hangs the JVM, and `ConcurrentHashMap.merge`

File I/O, Spring and the JDBC/build-tool stack are deliberately left out — they
are job skills rather than interview material — and the DSA ground is already
covered by the Problem Library and the Mastery track. See
[`JAVA_ROADMAP.md`](JAVA_ROADMAP.md), which also records how Part 10's exercises
are kept deterministic despite being about threads.

Each module carries a goal, four to six lessons, "predict the output" warm-ups,
fill-in-the-blank drills, fix-the-bug programs, coding challenges, a glossary,
a cheat sheet, a self-check, an end-of-module review quiz and a judged capstone
— **147 lessons and 633 judged exercises** in all, plus a **Practice** section
per module: five families of five variations each, where a family drills one
pattern and twists one dimension at a time, for **775 more problems**. Practice
is not required to complete a module. Every exercise runs through
the same `javac` → `java Main` judge as the rest of the app; Part 4's programs
declare their own classes above `Main` in the same file, which needed no change
to the judge.

Two rules shape it, mirroring the TypeScript course. **Nothing before its
module**: a gen-time linter scans every program and fails the build if it uses
an idea a later module teaches (no `StringBuilder` before module 8, no helper
methods before 9, no classes of your own before 11, no `interface` before 14,
no collections before 17, no type parameter of your own before 21, no wildcard
before 23, and no streams or lambdas at all — those belong to a later part of
`JAVA_ROADMAP.md`). And **expected outputs are computed, not typed**:
each test case's output comes from a Python mirror of the intended algorithm
inside the generator, the same trust model the problem bank uses.

The full 14-part plan, including what is built and what is still ahead
(OOP, exceptions, collections, generics, Java 8+, I/O, threads, DSA, Spring),
lives in [`JAVA_ROADMAP.md`](JAVA_ROADMAP.md).

You own the library. Add your own problems three ways:

1. **Author in-app** — Library → *New Problem* (full editor for statement,
   constraints, examples, hidden/example tests, hints, editorial, complexity).
2. **Import JSON** — Library → *Import* (an array of problems in the same shape
   as `seeds/problems.json`; re-import upserts by `slug` and preserves your
   progress and user-authored test cases).
3. **Export** the whole library to JSON for backup or editing.

---

## Feature coverage (against the spec)

**Fully built:** Dashboard (goals, streak, weakest topic, suggested next) ·
Problem Library with all filters (difficulty, topics, companies, status,
favorites, needs-review, weak-confidence, sorts) · Monaco editor (themes, font
size, minimap, word-wrap, find/replace, shortcuts, per-language + intellisense
toggle) · Code execution (Run/Submit, pass/fail, runtime, expected vs actual) ·
Test Case Manager (create/edit/delete/import/export + random & edge generators) ·
Markdown Notes with section templates · **Prerequisites checklist** (per-problem
concepts you check off as known, each expandable into "what it is" + "how it
helps *this* problem, with a deeper dive, Java-specific guidance, and a link to
the full lesson) · **Learn** section (a per-concept teaching page with a worked
example, code, and pitfalls; every section collapsible, and every Java and
TypeScript chapter pairs its fill-in-the-blank drills with a full coding
challenge) · **Java course** (twenty judged modules for someone past the
basics — arrays, strings, methods, OOP, exceptions and collections, each with
lessons, warm-ups, drills, fix-the-bug programs, a glossary, a cheat sheet, a
capstone and 25 practice variations) ·
**Backend Lab** (seven build-it-yourself projects taking a CRUD
HTTP API from `node:http` to routing, validation, persistence, querying, auth
and a layered, tested service — each with ordered instructions, a checkpoint per
step, judged drills, an acceptance checklist and curl commands to verify your
own server) · **6-Month Mastery** (two tracks — TypeScript and Java — each
sequencing the Learn catalog into 26 gated weeks: chapters, curated problems, a
build project with its own notes + code workspace, a shuffled multiple-choice
quiz drawn from a per-week bank, and a **judged coding final**; a week unlocks
the next only when chapters, quiz and final are all cleared, completed weeks
feed their material into the flashcard and revision queues, study time flows
into the heatmap, and pacing is tracked against a start date) ·
Spaced-Repetition Revision
(1→3→7→14→30→90 ladder, grade/snooze/manual) · Attempt History + Code
Comparison (first vs latest) · Progressive Hint System · Complexity Analyzer
(heuristic estimate vs optimal, with explanation) · Statistics (per
difficulty/topic, avg time, acceptance rate, heatmap, weekly/monthly, language
usage, weakest/strongest) · Learning Timeline + Recommendations · Interview Mode
(45-min timer, no hints/editorial, suggestions off, lock on expiry) · Random
Practice (weakness predicates) · Company Prep (grouped lists) · Solution Library
(multiple approaches with complexity) · full Offline Mode · Command palette
(Ctrl/Cmd+K) · dark/light themes · autosave & session restore.

**Scaffolded/extensible** (architecture supports; deferred by the agreed
"deep core + scaffold rest" scope): step-by-step Visual Debugger and Contest
Mode. The data model, execution seam, and tag system are designed so these slot
in without disruption.

---

## Database schema (SQLite, normalized)

`problems`, `tags` + `problem_tags` (topics/subtopics/companies unified),
`test_cases`, `notes`, `solutions`, `attempts`, `reviews`, `daily_sessions`,
`settings`, `meta`. Static problem content is separated from progress/execution
data, so re-importing a problem never clobbers your history. Foreign keys
cascade; indexes cover the hot query paths.

---

## Key design decisions & trade-offs

- **stdin/stdout judging** over per-language function harnesses: one universal
  contract, trivial to add languages, at the cost of asking solutions to parse
  input. Starter templates handle the parsing boilerplate.
- **Direct subprocess execution** (no container): correct for a personal,
  offline app running *your own* code; a timeout + temp-dir isolation guard
  against runaway processes. Not a hostile-code sandbox by design.
- **Reference-solution seed generator**: the surest way to honor "problem
  quality is paramount" — expected outputs are computed, never hand-typed.
- **Business logic mirrored in TS and Rust** (spaced repetition): the Rust side
  is authoritative for persistence; the TS copy powers instant UI and is
  unit-tested, keeping the two in lock-step.
- **Bundled Monaco (no CDN)**: larger bundle, but the editor works with zero
  network — non-negotiable for an offline-first app.
- **Single SQLite connection behind a mutex**: simplest correct model for a
  single-user desktop app; WAL mode keeps it responsive.

---

## Keyboard shortcuts

- `Ctrl/Cmd + K` — command palette (jump to any page or problem)
- `Ctrl/Cmd + Enter` — Run · `Ctrl/Cmd + Shift + Enter` — Submit
- Monaco defaults: `Ctrl/Cmd+F` find, `Ctrl/Cmd+H` replace, multi-cursor, etc.
