# Calc Roadmap — an expression language, modules 5-18

The plan for finishing **Calc**, the second project in the **Projects** track
(`tools/calc_project.py`). Modules 1-4 ship — phase 1 is complete — and 5-18 are
one-line skeletons waiting to be authored.

Companion to [`PROJECTS_ROADMAP.md`](PROJECTS_ROADMAP.md), which plans the same
track's first project. Both are **build** ladders — every module leaves the
application able to do one more thing than it could before — but they are
deliberately about different things, and the split is the reason a second
project exists at all:

| | Todo API | Calc |
|---|---|---|
| Subject | a service other programs talk to | a language that reads text |
| Data | arrives as strings from outside | designed by you, walked recursively |
| Hard part | contracts — status codes, validation, error envelopes | structure — precedence, trees, exhaustiveness |
| Type system | `type` and narrowing, mostly | discriminated unions, recursive types, `never` |
| Program shape | boots a real server, replays requests | reads stdin, prints an answer |

Someone who finishes both has written the two programs most jobs are made of.

**Status legend** — ✅ built and shipping · 🚧 partially built · ⬜ planned.

---

## Where it stands

**Built:** modules 1-4 — **16 steps, 42 judged exercises**, four revealable
references, and the project scaffolding (phases, scope table, brief, setup,
acceptance, manual test). Both program shapes are proven: `_plain` (module 1, and
the steps of 2-3 that have no input) and `_stdin` (module 2 on — every input is
its own test case, the empty string included).

| | |
|---|---|
| Content generator | `tools/calc_project.py` + one `calc_mNN_*.py` per module |
| Generated seed | `src-tauri/seeds/projects.json` (shared with the Todo API) |
| Rust model | unchanged — `Project` → `ProjectModule` → `BackendStep` already fit |
| UI | `src/pages/Projects.tsx`, route `/projects/calc-lang/:module` |
| Fast verifier | `python tools/verify_projects.py --starters --only calc-m` |
| Judge-level verifier | `cd src-tauri && cargo test --test verify_projects` |

### What landing project 2 actually cost

Less than expected, and the two things it did cost are worth recording.

**The lints had to become per-project.** `_lint_scope` and `_lint_syntax_taught`
read a scope table, and there was exactly one. That table is a *syllabus*, not a
track-wide fact: the Todo API introduces `.split(` in module 10 to pull an id out
of `/todos/7`, and Calc introduces it in module 18 to cut stdin into REPL lines.
Both lints now take the table as a parameter, and each project owns one.

**The track-level `harness_note` was Todo-shaped.** It described two program
shapes — "pure logic" and "a real server from module 4 on" — and that second
sentence is false on a project with no server. It now describes three, naming
which project each belongs to. Worth watching: this field renders on *every*
project page, so anything project-specific written into it is wrong somewhere.

Everything else was already general. `ProjectTrack.projects` is a list, the
overview grid renders the moment there is more than one, `authored=false` works
at project level as well as module level, and both verifiers walk every project
without knowing what a todo is. The one hardcoded assumption found was a `curl`
badge on the "try it yourself" section, now derived from whether the project has
a contract.

---

## The 18 modules

### Phase 1 — Scan (1-4) — ✅ **done**

Ends with: `1 + 2 * 3` becomes a list of tokens you can print, and `1 $ 2`
becomes an error naming the character and its column.

**1. What a token is** ✅ · `calc_m01_token.py` · 4 steps, 12 exercises
Token kinds as string literals · one type per kind · the discriminated union ·
narrowing on `kind` · factories · `JSON.stringify` and insertion order.
**The module's real payload** is the argument against `{ kind: string; value?:
number; op?: string }` — made concrete with `{ kind: "eof", value: 3, op: "+" }`,
a token the optional-field design says is fine.
**One design decision settled here on module 7's behalf:** operators are *one*
kind carrying a symbol, not four kinds. Precedence is a property of the symbol,
so grouping turns module 7's central question into one comparison rather than a
four-branch `if` in two functions.
**Why there is an `eof` token** is stated in the brief rather than left implicit:
it removes a `| undefined` from roughly thirty lines of module 6's parser.

**2. The scanner loop** ✅ · `calc_m02_scan.py` · 4 steps, 12 exercises
Arrays and `for … of` · stdin and `.trim()` · a cursor and `while` · `charAt` vs
`src[i]` · a digit's value from `indexOf` · narrowing a `string` to `Op`.
**The single-digit problem was solved with `DIGITS.indexOf(ch)`** — a digit's
position in `"0123456789"` is its value, and `-1` means "not a digit" — because
`Number` and `.slice` are module 3's. `.indexOf(` was added to the scope table at
2 for it. The limit is the point: `12` scans as two tokens, graded, and module 3
opens on it.
**Every branch moves the cursor itself**, four `i = i + 1`s rather than one at
the bottom of the loop, and step 3 says it is for module 3's sake.
**The skipped `$` is graded as today's behaviour**, the way the Todo API's module
9 grades its dishonest 500. The build's last test is `1 $ 2` → `1`, `2`, `eof`.
**The trap the module is built around:** `charAt` past the end is `""`, and
`DIGITS.indexOf("")` is **0**. So `while (i <= src.length)` grows a phantom
`number 0` before every `eof` — a clean, graded runtime fix, and the setup for
module 3's worse version of the same fact.

**3. Numbers, and tokens longer than one character** ✅ · `calc_m03_numbers.py` · 4 steps, 8 exercises
`slice` and the exclusive end · `Number` and `NaN` · `isDigit` · start / advance /
cut · guard order in `&&`.
**`Number` needs no `NaN` check here, and step 2 says exactly why**: the scanner
only hands it runs the inner loop accepted. The guarantee is the loop's, not
`Number`'s — accept a `.` or a `-` and it is gone. Both are in the stretch list.
**The hang is taught, not graded.** `isDigit("")` is true (module 2's trap), so an
inner loop with the length check missing or second never ends on an input ending
in a digit. The manual test has the learner do it on purpose and press Ctrl+C.
**`slice(start, i + 1)` only fails before an operator**, not before a space:
`Number("30 ")` is 30, because `Number` trims. The graded fix is `10/4`, where
the slice is `"10/"` and the value prints as `null` — and the prompt points out
that the passing inputs are the clue.

**4. When the input is not a program** ✅ · `calc_m04_errors.py` · 4 steps, 10 exercises
The four ways to fail · `ScanResult` with `ok: true` / `ok: false` · narrowing on
a boolean tag · the message format · `trimEnd` · the caller that must decide.
**Errors as values, as planned — and the compiler enforces it.** `result.tokens`
does not exist on a `ScanResult` until `result.ok` has been checked, so a main
program that forgets the failure does not compile. Step 4 grades exactly that
refusal as the module's one compile-time `fix` (`calc-m4-caller-fix1`).
**The format, now contract:** `error: unexpected '<ch>' at 1:<column>`, columns
from 1 (`i + 1`), line always `1` until programs have more than one line, first
error only. Printed on **stdout** so it can be judged; stderr and the exit code
are module 17's, for every kind of error at once.
**The column question this roadmap flagged was settled with `.trimEnd()`**,
gated at 4. `.trim()` removed leading spaces, so `  1 $ 2` would have reported
column 3 of text the user never typed; the build now grades column 5, and a
`fix` exercise is the `.trim()` version, which passes every test without leading
spaces. Module 17's caret depends on this.
**The skip from module 2 is gone** — graded as a `fix` whose starter is module
3's scanner.

### Phase 2 — Parse (5-8)

Ends with: a tree that already knows `1 + 2 * 3` is an addition whose right-hand
side is a multiplication.

**5. What a tree is** ⬜ · a type that refers to itself
*Introduces `: Expr`.* The second discriminated union, and the first recursive
one. *Risk: low, but the mental jump is real* — budget the whole module for
`type Expr = NumLit | Binary` where `Binary` holds two `Expr`s, and build trees
by hand before any parser exists. Same discipline as module 1: design the data,
then write the code that produces it.

**6. A parser with a cursor** ⬜ · peek, advance, expect
*The `eof` token from module 1 pays off here* — `peek()` returns a `Token`, never
`Token | undefined`, so nothing downstream carries a null check. Say so out loud;
it is a decision made two phases earlier that the learner can now see the value
of.

**7. Precedence, and why `1 + 2 * 3` is 7** ⬜ · two functions calling each other
*The centrepiece of the phase.* Also the module that cashes module 1's grouped
`op` kind: "does this operator bind tighter?" is one comparison against `t.op`.

**8. Parentheses and unary minus** ⬜ · recursion back to the top
*Adds the `lparen`/`rparen` kinds module 1 deliberately refused to add.* Closes
the grammar — the `primary` function calling back into `expression` is the loop
that makes the language infinite.

### Phase 3 — Evaluate (9-11)

Ends with: text in, a number out. A working calculator.

**9. Walking the tree** ⬜ · `switch` on the kind, recurse, return a number
*The easiest module in the project*, and saying so is the point: it is easy
because phase 2 built the right tree. Twenty lines.

**10. Exhaustiveness with `never`** ⬜ · the compiler proving you handled every node
*The module the whole project has been walking towards.* `const impossible: never
= node;` in the default branch turns "I added a node kind and forgot the
evaluator" from a bug report into a compile error. *Do this before phase 4*, not
after — phase 4 adds three node kinds, and the check is worth most on the module
that would otherwise have broken silently.

**11. Division, and the arithmetic that can fail** ⬜ · `1 / 0`, decided
*Small but not skippable.* JavaScript hands you `Infinity` and `NaN` for free;
a language that leaks them is a language whose errors surface three steps from
their cause. Decide, state the decision, enforce it.

### Phase 4 — A language, not a calculator (12-15)

Ends with: `let x = 4; x * x > 10` — variables, statements and booleans.

**12. Variables and an environment** ⬜ · a `Map`, and the name that is not in it
*`.get` returns `V | undefined`* — and here that `undefined` is not an annoyance,
it is the undefined-variable error. First place the project's error machinery
gets used by something other than the parser.

**13. Statements, and a program** ⬜ · `;`, and what a program's value is
*Contract change:* the parser's entry point stops returning an `Expr`. Small
module, but it is where "expression" and "program" stop being the same word.

**14. Booleans and comparison** ⬜ · the value type stops being `number`
*The hardest module in phase 4 and possibly the project.* Every arithmetic
operation now has to reject a boolean operand, which means a runtime type error
in a language whose errors were until now all syntax errors. *Budget a longer
module; consider splitting the value union into its own step.*

**15. `if` as an expression** ⬜ · a conditional that has a value
*Payoff module.* Needs `never` (module 10) to have been done properly, since it
adds a node kind — and if the compiler does not complain in exactly the right
places, module 10 was not finished.

### Phase 5 — Make it usable (16-18)

Ends with: `error: unexpected ')' at 1:7`, a caret under the character, and a
REPL.

**16. Line and column on every token** ⬜ · carry the position or you cannot report it
*Retrofit module, and deliberately so.* The scanner has been throwing positions
away for fifteen modules; adding them touches every factory and nothing else,
which is the argument for module 1's factories made concrete. **Say that out
loud in the step** — it is the clearest payoff in the project for a decision that
looked like ceremony at the time.

**17. Error messages that point at the problem** ⬜ · the caret, and `try`/`catch`
*Introduces `throw`, `try`, `catch` — the only place they appear.* The
module's argument is the comparison: results as values everywhere inside, one
`try` at the boundary, and a reason for each choice. Also where exit codes get
decided, because a tool that prints an error and exits 0 cannot go in a script.

**18. A REPL, and a test suite you wrote** ⬜ · stdin line by line, zero dependencies
*Closes the project.* The test runner is written by hand, which doubles as the
argument for what a test framework actually does. *Introduces `.split(`, `=>` and
`.map(` — late, and correctly so: nothing before this needed any of them.*

---

## Suggested batching

Each batch ends green and committable.

| Batch | Modules | Why this grouping |
|---|---|---|
| **A** ✅ | — | Project entry, phases, scope table, skeletons, per-project lints |
| **B** ✅ | 1 | The token union — proves the shape end to end |
| **C** ✅ | 2-4 | Phase 1. Module 2 brought stdin; module 4 fixed the error format |
| **D** | **5-8** ← next | Phase 2 — the parser. Module 5 is the recursive-type jump |
| **E** | 9-11 | Phase 3 — short, and module 10 is the project's punchline |
| **F** | 12-15 | Phase 4. Module 14 is the one to think about first |
| **G** | 16-18 | Phase 5 — positions, messages, REPL |

**Module 14 is the one to settle before batch F.** Batch D can start now.

### What phase 1 established that the parser can rely on

* **`scan` returns a `ScanResult`**, and module 6's parser receives the success
  member's `tokens` — which always end in exactly one `eof`, so `peek()` can
  return a `Token`, never `Token | undefined`, exactly as module 1 promised.
* **The error format is fixed.** A parse error should read the same way —
  `error: unexpected ')' at 1:5`, `error: expected a number at 1:4` — which means
  **the parser needs positions**, and tokens do not carry them until module 16.
  Either module 6 passes the scanner's cursor positions along with the tokens, or
  parse errors cannot name a column until 16. Decide before module 6.
* **A generic `Result<T>` is in the stretch list, not the code.** The parser will
  want `{ ok: true; expr: Expr } | { ok: false; error: string }`, and module 6 is
  the natural place to notice the two unions have the same shape.

### What modules 2-3 established that module 4 can rely on

* **The scanner's `else` branch is the only place an unknown character goes.**
  Module 4 replaces exactly that branch; nothing else in `scan` needs to know.
* **The cursor `i` at that branch is the character's position — in the
  *trimmed* source.** `main` calls `.trim()`, which removes leading whitespace
  too, so for `echo '  1 $ 2'` the `$` is at `i + 1 = 3` but column 5 of what the
  user typed. Module 4 has to decide this before the format becomes contract:
  trim only the end (`.trimEnd()` is not yet in the scope table), or report
  columns in the trimmed text and say so. The first is almost certainly right,
  since module 17 draws a caret under the original line.
* **Every exercise program ends in `_C2_MAIN`**, printing one JSON token per
  line. Module 4 changes what `scan` returns, so it is the first module to
  change `main` as well — it has to print either the tokens or the error.
* **The trimmed source has no newlines**, so every position is on line 1 until
  module 13 introduces `;`-separated statements and module 16 carries positions.

---

## Constraints every module must satisfy

Same as the Todo API's, against `_CALC_SCOPE_RULES` rather than
`_TODO_SCOPE_RULES`:

* **Nothing before its module**, enforced by `_lint_scope`.
* **Every token is taught**, enforced by `_lint_syntax_taught`.
* **Erasable syntax only** — `enum`, `namespace` and parameter properties are
  banned at module 999.
* **Errors are values until module 17.** An uncaught `throw` in a judged program
  is a crash, and a crash is not an answer.
* **Error text is contract.** Decided in module 4, unchanged afterwards except
  where module 17 deliberately extends it.
* **Expected output is computed, not typed** — same trust model as the rest of
  the app.
* **Both verifiers must pass**: `python tools/verify_projects.py --starters` and
  `cd src-tauri && cargo test --test verify_projects`.

### Adding module N

1. Write `tools/calc_mNN_topic.py` — it appends one `_pmod(…)` to
   `_CALC_MODULES` and may use any helper from `projects_track.py`.
2. Add it to `_CALC_MODULE_FILES` **in module order**, and delete the matching
   `_pskel` line from the skeleton list below it.
3. Add that module's new syntax to `_CALC_SCOPE_RULES`, and make sure the
   module's `syntax` primer teaches each token — `_lint_syntax_taught` will tell
   you if not.
4. `python tools/gen_seed.py && python tools/verify_projects.py --starters`

### The trap worth knowing

`_lint_scope` scans **program text, not code** — comments and strings included.
Module 1's programs may not contain the word `never` (module 10) or `case `
(module 9) anywhere, even in prose inside a comment, and the same widens as the
table grows. Where teaching text inside a program needs an ellipsis, use the
Unicode `…`, exactly as the Todo API's early modules do.

And **`=>` is gated at 18 in this project**, unlike the Todo API's 3. Every array
method that takes a callback — `find`, `findIndex`, `filter`, `map` — is out of
reach until then, which is why modules 2-3 walk arrays and strings with `while`
and `for … of` and never a callback.

---

## What "done" looks like

One language · 18 modules · 5 phases · roughly 140 judged exercises · a scanner,
a parser, an evaluator and error messages a stranger could act on · and a learner
who has met the discriminated union enough times to reach for one unprompted.
