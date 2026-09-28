# Calc Roadmap — an expression language, modules 1-18

The plan — now the record — for **Calc**, the second project in the
**Projects** track (`tools/calc_project.py`). **All 18 modules ship.** The
roadmap is complete; what follows says what each module built and what it
decided, so the next person to extend the language knows which decisions are
load-bearing.

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

**Built:** all 18 modules — **72 steps, 165 judged exercises**, eighteen
revealable references (each one the learner's whole `calc.ts` at that point, and
each one type-checked), and the project scaffolding (phases, scope table, brief,
setup, acceptance, manual test). Three program shapes: `_plain` (hand-built
values, no input), `_stdin` (every input its own test case), and — module 18
only — a program that reads stdin a line at a time with `node:readline`.

| | |
|---|---|
| Content generator | `tools/calc_project.py` + one `calc_mNN_*.py` per module |
| Expected-output oracle | `tools/calc_oracle.py` — see below |
| Generated seed | `src-tauri/seeds/projects.json` (shared with the Todo API) |
| Rust model | unchanged — `Project` → `ProjectModule` → `BackendStep` already fit |
| Ambient types | `src-tauri/tslib/poodcode-env.d.ts` gained `process` and `node:readline` (modules 17-18) |
| UI | `src/pages/Projects.tsx`, route `/projects/calc-lang/:module` |
| Fast verifier | `python tools/verify_projects.py --starters --only calc-m` |
| Judge-level verifier | `cd src-tauri && cargo test --test verify_projects` |

### The oracle

From module 5 on, expected outputs are trees, numbers, error messages with
columns and three-line caret reports — too easy to hand-type wrong in a way that
happens to agree with a wrong TypeScript solution. So `tools/calc_oracle.py` is a
**second, independent implementation of the language in Python**, with a
feature gate per module (`m >= 8` means brackets exist, `m >= 16` means errors
carry positions, and so on). `_calc(src, m)` is the stdout of module *m*'s judged
program; `_ctests(m, inputs)` builds a test list from it. Every expected output
from module 6 on comes from there — module 5's hand-built trees are checked
against module 8's parser — so the verifier is comparing two implementations in
two languages, and neither is trusted alone.

`_jsnum` mirrors JavaScript's number-to-string rules exactly (shortest
round-trip digits, exponent above 1e21 and below 1e-6), which is what lets the
oracle predict `2.5`, `0.3333333333333333` and `1e+299`.

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

### Phase 2 — Parse (5-8) — ✅ **done**

Ends with: a tree that already knows `1 + 2 * 3` is an addition whose right-hand
side is a multiplication.

**5. What a tree is** ✅ · `calc_m05_tree.py` · 4 steps, 10 exercises
`type Expr = NumLit | Binary`, factories, recursion, base cases, associativity.
**Every program is `_plain`** — trees built by hand, no parser — exactly as
planned. **`show` prints S-expressions**, `(+ 1 (* 2 3))`, and that format became
the judged output of modules 6-8; `(neg 3)` was reserved here for module 8 so
negation can never read as subtraction. Node tag is `"num"`, not the token's
`"number"`, so a token can never pass for a node. The hand-built trees' expected
output is module 8's parser's view of the same source, via the oracle.

**6. A parser with a cursor** ✅ · `calc_m06_cursor.py` · 4 steps, 12 exercises
`Parser = { tokens; pos }`, `peek`/`advance`, `describe`, the end-of-input check.
**The grammar is a single number** so the machinery gets the module to itself;
`1 + 2` is refused, graded, and module 7 opens on it. **The eof payoff is said
out loud:** `peek` is the only function that ever checks for `undefined`.
**The position question was decided: parse errors say what, not where** —
`error: unexpected '+'`, `error: unexpected end of input` — until module 16. The
cost is stated in step 2 as a cost. **`type Failure = { ok: false; error: string }`
is named here**, so module 16 later changed what an error is in one place. The
generic `Result<T>` stayed a stretch item.

**7. Precedence, and why `1 + 2 * 3` is 7** ✅ · `calc_m07_precedence.py` · 4 steps, 7 exercises
**One function per precedence level** (`parseSum` → `parseProduct` →
`parsePrimary`), chosen over precedence climbing because the grammar can be read
straight off the code and module 14 then adds a level as one more function.
Module 1's grouped `op` kind makes each level's test one kind check and a look at
the symbol. **The graded associativity bug** is recursing into your own level for
the right operand (`(/ 8 (/ 4 2))`), with the point made that `+`/`*`-only tests
can never catch it.

**8. Parentheses and unary minus** ✅ · `calc_m08_parens.py` · 4 steps, 8 exercises
`lparen`/`rparen`, a `neg` node, a unary rung between product and primary, and
**`parseExpr` introduced as the name for the top of the grammar** — which is why
module 14 changed one line. **The union grows and `describe`'s fall-through
breaks silently** (`1 + )` → "end of input"); graded as a runtime fix and used as
module 10's opening case. `expected ')' but found …` messages arrive here, as
module 4's table promised. `parseUnary` recurses on itself deliberately — prefix
operators are right-associative — and the step says why that is not module 7's
bug.

### Phase 3 — Evaluate (9-11) — ✅ **done**

Ends with: text in, a number out. A working calculator.

**9. Walking the tree** ✅ · `calc_m09_walk.py` · 4 steps, 8 exercises
`switch`/`case` (gated here) for `describe` and `evaluate`; `arithmetic` split out
so modules 11 and 14 change operators without touching the walk. **Honest about
the accidental exhaustiveness check** (`TS2366` fires on a missing case in a
value-returning switch) — module 10 then shows where it stops working. `show`
leaves the main program. `1 / 0` is left printing `Infinity` on purpose, and the
module ends by pointing at it.

**10. Exhaustiveness with `never`** ✅ · `calc_m10_never.py` · 4 steps, 7 exercises
Three places the accidental check goes quiet — code after the switch, any
`default`, a `void` function — then `const impossible: never = x;` on every
switch (`describe`, `evaluate`, `arithmetic`). Graded: a `label` switch that
compiles with a missing case, and `default: return 0;` evaluating `-3` to zero.
One deliberate compile-time `fix` (`calc-m10-every-fix1`).

**11. Division, and the arithmetic that can fail** ✅ · `calc_m11_arithmetic.py` · 4 steps, 9 exercises
**Decided:** `x / 0` is `error: division by zero`, checked before dividing so
`0 / 0` gets it too; anything non-finite — overflow or a 400-digit literal — is
`error: number too large`, via one `checked` function (`Number.isFinite`, gated
here). The evaluator can never produce `NaN`. `evaluate` returns an `EvalResult`;
operand order now decides which error wins (graded), and `${evaluate(…)}`
compiling to `[object Object]` is graded as the place the result type's guarantee
stops.

### Phase 4 — A language, not a calculator (12-15) — ✅ **done**

Ends with: `let x = 4; x * x > 10` — variables, statements and booleans.

**12. Variables and an environment** ✅ · `calc_m12_vars.py` · 4 steps, 9 exercises
`ident` tokens, a `var` node (factory `variable` — `var` is reserved), and
`type Env = Map<string, number>` threaded through `evaluate`. `Map.get`'s
`undefined` is the `undefined variable 'y'` error; treating it as zero is graded
as the bug. **`let` moved to module 13**, because bindings need statements —
module 12's programs start with `day`, `week` and `dozen` in the environment, and
the brief says so. Module 10's first real dividend: adding the two types produces
a `never` error in exactly `describe` and `evaluate`.

**13. Statements, and a program** ✅ · `calc_m13_statements.py` · 4 steps, 9 exercises
`let`, `=` and `;`; `Stmt = LetStmt | ExprStmt`; `parseProgram` replaces `parse`.
**Decided:** a program's value is its last statement's; a `let`'s value is what it
bound; a trailing `;` is allowed; statements run in order against an environment
that starts empty; a failing `let` binds nothing. Keywords are recognised after
the whole word is read, which is what makes them reserved. `runProgram` starts
from a failure no user can see, and the step names that gap between the parser's
guarantee and the type.

**14. Booleans and comparison** ✅ · `calc_m14_booleans.py` · 4 steps, 9 exercises
**`type Value = number | boolean` got a step of its own**, first, as the roadmap
suggested. `<`, `>`, `==` on a new level below `+`; `true`/`false` keywords; a
one-character lookahead for `==`. **Rules:** arithmetic, `<` and `>` need numbers
(`cannot apply '*' to a boolean`), `==` needs matching types (`cannot compare a
number with a boolean`), negation needs a number. `1 < 2 < 3` is a type error.
`arithmetic` became `apply`, whose `never` default still works because the early
`==` return narrowed `op` — "narrowing composes". The compiler forces every rule
but one: `==` across types, which is the graded runtime fix.

**15. `if` as an expression** ✅ · `calc_m15_if.py` · 4 steps, 8 exercises
`if … then … else …` as a primary, `else` mandatory (no dangling else), condition
must be a boolean (no truthiness), **only the chosen branch evaluated** (graded),
and each branch a full expression so the last one reaches right (graded). The
module 10 exam: the four new types produce `never` errors in `describe` and
`evaluate` and **nowhere else** — the deliberate compile-time `fix` is built on
that list.

### Phase 5 — Make it usable (16-18) — ✅ **done**

Ends with: `error: unexpected ')' at 1:5`, a caret under the character, and a
REPL.

**16. Line and column on every token** ✅ · `calc_m16_positions.py` · 4 steps, 9 exercises
`Pos` on every token and node, added through the factories — **and step 1 says
out loud that this is module 1's payoff.** The scanner tracks `line`/`lineStart`;
`\n` starts a line and `\r` is whitespace. Errors became data,
`CalcError = { message; pos }`, built by `fail` and formatted once by
`formatError`; every error gained ` at L:C`, the extension module 6 promised.
**Where errors point:** tokens at themselves, `eof` just past the end, arithmetic
and type errors at the operator, names at the name. The program is written out in
full in this module's file rather than derived, since the retrofit touched
everything.

**17. Error messages that point at the problem** ✅ · `calc_m17_messages.py` · 4 steps, 10 exercises
The caret (`.repeat(`), found with two-argument `indexOf` since `.split(` is 18's.
**The argument, as planned:** user mistakes stay values (exit 1); impossibilities
throw — `assertNever(x: never): never` and `peek` past the end — and one
`try`/`catch` at the edge turns anything thrown into `error: internal error: …`
(exit 2). The catch is exercised by an exception the program never threw: ten
thousand nested brackets overflow the stack. Judged programs print the exit code
as a last line (`exit 1`); the reference uses `console.error` and
`process.exitCode`. `instanceof`, `console.error(` and `process.exitCode` were
added to the scope table here.

**18. A REPL, and a test suite you wrote** ✅ · `calc_m18_repl.py` · 4 steps, 8 exercises
**The REPL uses `node:readline`, not `readFileSync(0).split("\n")`** — a REPL that
waits for Ctrl+D is not a REPL — so `rl.on("line", (line) => …)` is the project's
first callback, and `createInterface(` and `.on(` joined `=>` at 18. One
environment per session, a fresh one per test case; the environment has been a
parameter since module 12, so neither needed a change to the language. The test
runner is forty lines — cases, a comparison, the first differing line via
`.split(`, a summary via `.map(` — and the graded bug is a suite sharing one
environment between cases. The finished `calc.ts` picks its mode: `--test`, a TTY
REPL with a prompt, or one piped program.

---

## How it was batched

Each batch ended green: both verifiers passing.

| Batch | Modules | Why this grouping |
|---|---|---|
| **A** ✅ | — | Project entry, phases, scope table, skeletons, per-project lints |
| **B** ✅ | 1 | The token union — proves the shape end to end |
| **C** ✅ | 2-4 | Phase 1. Module 2 brought stdin; module 4 fixed the error format |
| **D** ✅ | 5-8 | Phase 2 — the parser, and the oracle that checks it |
| **E** ✅ | 9-11 | Phase 3 — evaluation, `never`, and the arithmetic decision |
| **F** ✅ | 12-15 | Phase 4 — module 14's `Value` union settled first, as planned |
| **G** ✅ | 16-18 | Phase 5 — positions, messages, REPL; ambient `process`/`readline` types |

### The decisions this roadmap left open, and how they were settled

* **Positions in parse errors (flagged before module 6).** Not threaded through
  the parser. Parse errors named the token but no column from module 6 to 15;
  module 16 put a position on every token and node through the factories, and
  every error gained ` at L:C`. The inconsistency was stated as a cost where it
  was taken.
* **`Result<T>` (flagged before module 6).** Stayed a stretch item. Instead the
  failure half was named once, `type Failure`, in module 6 — which is what let
  module 16 change what an error *is* in one place. By module 13 there are five
  result types; step 3 of that module points at the pressure rather than hiding
  it.
* **Module 14 (flagged before batch F).** `Value` got its own first step; `==`
  requires matching types; no coercion anywhere, including `if` conditions in
  module 15.
* **Module 12's `let x = 4`.** Moved to module 13, because a binding needs a
  statement to live in. Module 12's programs start with three names already
  bound, and say so.
* **The REPL's input.** `node:readline`, not `readFileSync(0).split("\n")` —
  the second waits for Ctrl+D. `.split(` still arrives in module 18, in the test
  runner.

---

## Constraints every module satisfies

Same as the Todo API's, against `_CALC_SCOPE_RULES` rather than
`_TODO_SCOPE_RULES`:

* **Nothing before its module**, enforced by `_lint_scope`.
* **Every token is taught**, enforced by `_lint_syntax_taught`.
* **Erasable syntax only** — `enum`, `namespace` and parameter properties are
  banned at module 999.
* **Errors are values**, everywhere a user can cause them — even after module 17,
  where `throw` is reserved for impossibilities and caught once at the edge.
* **Error text is contract.** Decided in module 4; extended with ` at L:C` for
  every error in module 16 and with the caret in module 17.
* **Expected output is computed, not typed** — by `tools/calc_oracle.py`, an
  independent implementation, from module 6 on.
* **Both verifiers pass**: `python tools/verify_projects.py --starters` and
  `cd src-tauri && cargo test --test verify_projects`.

### Extending Calc

The modules' own stretch lists are the natural next features (`%`, `<=`,
functions, a formatter). For a new *module*:

1. Write `tools/calc_mNN_topic.py` — it appends one `_pmod(…)` to
   `_CALC_MODULES` and may use any helper from `projects_track.py`, the code
   constants of earlier modules (`_C16_TOKENS`, `_C13_PARSE_STMT`, …), and the
   oracle.
2. Add it to `_CALC_MODULE_FILES` **in module order**.
3. Add its new syntax to `_CALC_SCOPE_RULES`, and teach each token in the
   module's `syntax` primer — `_lint_syntax_taught` will tell you if not.
4. Teach the oracle the feature behind a `m >= N` gate, and build every test list
   with `_ctests(N, inputs)`.
5. `python tools/gen_seed.py && python tools/verify_projects.py --starters --only calc-mN`

### The traps worth knowing

`_lint_scope` scans **program text, not code** — comments and strings included.
A program before module 10 may not contain the word `never` anywhere, even in a
comment, and none before module 9 may contain `case `. Where teaching text inside
a program needs an ellipsis, use the Unicode `…`.

**`=>` is gated at 18 in this project**, unlike the Todo API's 3, so no module
before 18 uses a callback or an array method that takes one.

When deriving a module's code from an earlier module's by string replacement,
**anchor the replacement precisely**: `"    } else {\n"` also matches inside a
more deeply indented `      } else {`, and module 13's scanner briefly grew its
`=` branch inside the keyword check that way.

---

## What "done" looks like — and is

One language · 18 modules · 5 phases · **165 judged exercises** · a scanner, a
recursive-descent parser, an evaluator over a discriminated-union tree, error
messages with a caret that a stranger could act on, a REPL and a hand-written
test suite · and a learner who has met the discriminated union enough times to
reach for one unprompted.
