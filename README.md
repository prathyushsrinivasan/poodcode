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
│  └─ seeds/problems.json      # the bundled original problem set
│
└─ tools/gen_seed.py           # generator that AUTHORS seeds/problems.json
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
python tools/gen_seed.py       # writes src-tauri/seeds/problems.json
```

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
example, Java code, and pitfalls) · Spaced-Repetition Revision
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
