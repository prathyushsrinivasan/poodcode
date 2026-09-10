# Calc Roadmap — an expression language, modules 2-18

The plan for finishing **Calc**, the second project in the **Projects** track
(`tools/calc_project.py`). Module 1 ships; 2-18 are one-line skeletons waiting to
be authored.

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

**Built:** module 1 — **4 steps, 12 judged exercises**, a revealable reference,
and the project scaffolding (phases, scope table, brief, setup, acceptance,
manual test). The `_plain` program shape is proven; `_stdin` lands with module 2.

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

### Phase 1 — Scan (1-4) — 🚧 **1 done, 2-4 outstanding**

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

**2. The scanner loop** ⬜ · `while`, a cursor, `.charAt`, push onto an array
*Also where stdin arrives* — from here every exercise is driven by real input,
so a single exercise can be checked against `1 + 2`, `7` and the empty string at
once. *Worth teaching explicitly:* `src[i]` is `string | undefined` under
`noUncheckedIndexedAccess` while `src.charAt(i)` is `string`. That is a real
choice with a real trade-off, not a style preference.

**3. Numbers, and tokens longer than one character** ⬜ · digit runs, `.slice`,
`Number`
*The first lookahead in the project.* A scanner that consumes one character per
iteration cannot read `123`, and the fix — remember where the token started,
advance while the character is still a digit, slice — is the shape every
multi-character token uses afterwards.

**4. When the input is not a program** ⬜ · a result union, not an exception
*Introduces `ok: true` as a literal type.* **This is the module that decides the
project's error strategy**, and it decides it against exceptions: failures are
values until module 17. Two reasons — an uncaught throw in a judged program is a
crash rather than an answer, and returning failures forces every caller to say
what it does about them, which is most of what phase 5 is about.
*Also decides the error text format*, which is then contract for fourteen
modules. Get `error: unexpected '$' at 1:3` right here.

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
| **C** | 2-4 | Phase 1. Module 2 brings stdin; module 4 fixes the error format |
| **D** | 5-8 | Phase 2 — the parser. Module 5 is the recursive-type jump |
| **E** | 9-11 | Phase 3 — short, and module 10 is the project's punchline |
| **F** | 12-15 | Phase 4. Module 14 is the one to think about first |
| **G** | 16-18 | Phase 5 — positions, messages, REPL |

**Module 4 is the one to settle before starting batch C** (the error format is
contract for fourteen modules), and **module 14 before batch F**.

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

---

## What "done" looks like

One language · 18 modules · 5 phases · roughly 140 judged exercises · a scanner,
a parser, an evaluator and error messages a stranger could act on · and a learner
who has met the discriminated union enough times to reach for one unprompted.
