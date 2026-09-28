# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 18 — A REPL, and a test suite you wrote.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Builds on module 17's program. Closes the project.
#
# THE REPL reads stdin a line at a time with `node:readline` — the first
# callback in the project, which is why `=>` was gated here (the scope table
# says so). Decided and graded:
#   * each line is its own program (`at 1:C`, a caret under that line);
#   * ONE environment outlives every line — `let x = 4` on one line, `x * x` on
#     the next (the fix `calc-m18-session-fix1` makes a fresh Map per line);
#   * blank lines print nothing; an error prints its report and the session
#     carries on; bindings made before a failure on the same line stay (module
#     13 asked the learner to decide this; here it becomes observable).
#
# THE TEST SUITE is written by hand, with no framework: a list of cases, a loop,
# a comparison, a report of the first differing line (`.split(`), and a summary
# (`.map(`). Expected texts in the cases are computed by the oracle, like every
# other expected output. The graded fix is TEST ISOLATION: a suite sharing one
# environment between cases lets `let x = 4` leak into the case that expects
# `x` to be undefined.
#
# JUDGED vs REAL. A judged program cannot be interactive, so the REPL exercises
# call `repl(...)` directly on piped stdin, without a prompt; the suite exercises
# ignore stdin. The reference — the finished calc.ts — picks its mode:
# `--test` runs the suite, a terminal on stdin gets the REPL with a `> ` prompt,
# and anything piped is one whole program, as in module 17.
# ---------------------------------------------------------------------------

import json as _c18json

_C18_IMPORTS = ('import { readFileSync } from "node:fs";\n'
                'import { createInterface } from "node:readline";\n')


def _c18_program(*parts):
    return _C18_IMPORTS + "\n" + _cjoin(*parts)


_C18_BODY = (
    _C16_TOKENS, _C16_ERRORS, _C17_NEVER_FN, _C16_SCAN, _C16_TREE, _C13_STMTS, _C17_STATE,
    _c17_defaults(_C16_DESCRIBE), _C16_PRIMARY, _C16_UNARY, _C16_PRODUCT, _C16_SUM,
    _C16_COMPARISON, _C13_PARSE_STMT, _C13_PARSE_PROGRAM, _C16_RESULT, _C14_ENV,
    _c17_defaults(_C16_EVAL), _c17_defaults(_C16_APPLY), _c17_defaults(_C16_EXECUTE),
    _C17_REPORT, _C17_RUN, _C17_BOUNDARY,
)

_C18_REPL = """function repl(env: Env): void {
  const rl = createInterface({ input: process.stdin });
  rl.on("line", (line) => {
    if (line.trim() === "") {
      return;
    }
    console.log(main(line.trimEnd(), env).text);
  });
}

repl(new Map());
"""


def _c18_repl(repl=_C18_REPL):
    return _c18_program(*_C18_BODY, repl)


_C18_REPL_FULL = _c18_repl()

_C18_SESSIONS = [
    "let x = 4\nx * x\ny + 1\n\nlet y = x + 1\ny * 2",
    "1 + 2 * 3\n1 + )\nlet a = 1; a / 0\na\nif a > 0 then 10 else 20",
    "   \n2 < 3\ntrue * 2\nlet t = 2 < 3\nif t then 1 else 2",
    "let n = 10\nlet n = n * 2\nn",
    "",
]
_C18_REPL_TESTS = _ctests(18, _C18_SESSIONS)

# --- The test suite ---------------------------------------------------------
_C18_CASE_SRCS = ["1 + 2 * 3", "(1 + 2) * -3", "10 / 4", "let x = 4; x * x", "x",
                  "let x = 4; x * x > 10", "if 2 < 3 then 10 else 20",
                  "if false then 1 / 0 else 2", "1 / 0", "1 + )", "y + 1", "true * 2"]


def _c18_cases():
    lines = ["type Case = { src: string; want: string };", "", "const CASES: Case[] = ["]
    for s in _C18_CASE_SRCS:
        want = _c_run(s, 18, {})[0]
        lines.append(f"  {{ src: {_c18json.dumps(s)}, want: {_c18json.dumps(want)} }},")
    lines.append("];")
    return "\n".join(lines) + "\n"


_C18_CASES = _c18_cases()

_C18_CHECK = """function check(c: Case): boolean {
  const got = main(c.src, new Map()).text;
  if (got === c.want) {
    return true;
  }
  const gotLines = got.split("\\n");
  const wantLines = c.want.split("\\n");
  let i = 0;
  while (i < gotLines.length && i < wantLines.length && gotLines[i] === wantLines[i]) {
    i = i + 1;
  }
  console.log(`FAIL ${c.src}`);
  console.log(`  line ${i + 1}`);
  console.log(`  want: ${JSON.stringify(wantLines[i])}`);
  console.log(`  got:  ${JSON.stringify(gotLines[i])}`);
  return false;
}
"""

_C18_SUMMARY = """const results = CASES.map((c) => check(c));
let passed = 0;
for (const ok of results) {
  if (ok) {
    passed = passed + 1;
  }
}
console.log(`${passed} passed, ${results.length - passed} failed`);
"""


def _c18_suite(check=_C18_CHECK, summary=_C18_SUMMARY, cases=_C18_CASES):
    return _c18_program(*_C18_BODY, cases, check, summary)


_C18_SUITE_FULL = _c18_suite()
_C18_SUITE_OUT = f"{len(_C18_CASE_SRCS)} passed, 0 failed"
_C18_SUITE_TESTS = [("", _C18_SUITE_OUT)]

# --- The finished calc.ts: three modes --------------------------------------
_C18_REAL_TAIL = """function repl(env: Env): void {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  rl.setPrompt("> ");
  rl.prompt();
  rl.on("line", (line) => {
    if (line.trim() !== "") {
      const outcome = main(line.trimEnd(), env);
      if (outcome.code === 0) {
        console.log(outcome.text);
      } else {
        console.error(outcome.text);
      }
    }
    rl.prompt();
  });
}

function runTests(): void {
  const results = CASES.map((c) => check(c));
  let passed = 0;
  for (const ok of results) {
    if (ok) {
      passed = passed + 1;
    }
  }
  console.log(`${passed} passed, ${results.length - passed} failed`);
  if (passed !== results.length) {
    process.exitCode = 1;
  }
}

if (process.argv[2] === "--test") {
  runTests();
} else if (process.stdin.isTTY) {
  repl(new Map());
} else {
  const outcome = main(readFileSync(0, "utf8").trimEnd(), new Map());
  if (outcome.code === 0) {
    console.log(outcome.text);
  } else {
    console.error(outcome.text);
  }
  process.exitCode = outcome.code;
}
"""

_C18_REFERENCE = _c18_program(*_C18_BODY, _C18_CASES, _C18_CHECK, _C18_REAL_TAIL)


_C18_WHY = (
    "`calc.ts` answers one program and exits. That is right for a script and "
    "wrong for a person trying things out, who wants to type `let x = 4`, see "
    "`4`, type `x * x`, see `16` — a **REPL**, read-eval-print loop, the first "
    "thing anyone reaches for with a new language. It needs stdin a line at a "
    "time, which is the first callback this project has needed, and one "
    "environment that outlives every line. And a language you intend to keep "
    "changing needs tests: this module writes a test runner by hand, which turns "
    "out to be a loop and a comparison — and is the best explanation there is of "
    "what a test framework actually does for you."
)

_C18_BRIEF = """
### The whole module in one line

`node calc.ts` with nothing piped in opens a `> ` prompt that remembers your
variables between lines; `node calc.ts --test` runs a test suite you wrote with
no framework.

### A REPL

```
$ node calc.ts
> let x = 4
4
> x * x
16
> y + 1
error: undefined variable 'y' at 1:1
  y + 1
  ^
> let y = x + 1
5
```

Read a line, evaluate it, print the result, loop. Three decisions make it work:

| Decision | Why |
|---|---|
| each line is its own program | positions are `1:C`, and the caret is under the line you just typed |
| one environment for the whole session | `let x = 4` on one line, `x` on the next |
| an error ends the line, not the session | a typo should not throw away everything you defined |

### Why `readFileSync` cannot do it

`readFileSync(0, "utf8")` reads stdin **until it ends** — for a terminal, until
you press Ctrl+D. A REPL has to answer each line as it arrives. Node's built-in
`node:readline` does exactly that, calling a function you give it once per line:

```ts
rl.on("line", (line) => {
  console.log(main(line.trimEnd(), env).text);
});
```

That `(line) => { … }` is an **arrow function** — the first callback in this
project, and the reason `=>` waited until now.

### A test suite you wrote

```ts
const CASES: Case[] = [
  { src: "1 + 2 * 3", want: "7" },
  { src: "1 + )", want: "error: unexpected ')' at 1:5\\n  1 + )\\n      ^" },
  …
];
```

A list of inputs and expected outputs, a loop that runs each through `main`, a
comparison, and a line saying how many passed. That is all a test framework is at
its core. Writing it once yourself makes every framework you meet afterwards
legible.

### One file, three modes

The finished `calc.ts` looks at how it was started: `--test` runs the suite, a
terminal gets the REPL, and anything piped in is one whole program, exactly as
in module 17. The judged exercises call the REPL and the suite directly, since a
judge cannot type at a prompt.
"""

_C18_SYNTAX = [
    _syn(
        "rl.on(\"line\", (line) => { … });",
        "Register a function to be called for every line of input. `(line) => { … }` "
        "is an **arrow function** — a function written inline, with no name.",
        """
rl.on("line", (line) => {
  console.log(line.length);
});
""",
        "`line`'s type comes from `on`'s declaration: TypeScript knows a `\"line\"` "
        "listener receives a string, so the parameter needs no annotation.",
    ),
    _syn(
        "const rl = createInterface({ input: process.stdin });",
        "Wrap stdin in a line reader from `node:readline`. It calls your `\"line\"` "
        "listener as each line arrives, and ends when stdin does.",
        """
import { createInterface } from "node:readline";

const rl = createInterface({ input: process.stdin, output: process.stdout });
rl.setPrompt("> ");
rl.prompt();
""",
        "With `output` given it can print a prompt; the judged exercises leave it "
        "out, since nobody is typing.",
    ),
    _syn(
        "const gotLines = got.split(\"\\n\");",
        "`s.split(sep)` cuts a string at every `sep` into an array of pieces.",
        """
"a\\nb\\nc".split("\\n");     // ["a", "b", "c"]
"abc".split("\\n");         // ["abc"]
""",
        "Under `noUncheckedIndexedAccess`, `gotLines[i]` is `string | undefined` — "
        "the loop's length checks are what keep it in range.",
    ),
    _syn(
        "const results = CASES.map((c) => check(c));",
        "`xs.map(f)` makes a new array by calling `f` on every element — here, a "
        "`boolean[]` of pass/fail, one per case.",
        "",
        "It is the `for … of` loop that builds an array, written as one "
        "expression. Every array method that takes a callback needed `=>`, which "
        "is why none appeared before this module.",
    ),
    _syn(
        "if (process.argv[2] === \"--test\") { … }",
        "`process.argv` is the command line as an array of strings — `node`, the "
        "script, then any arguments.",
        "",
        "`node calc.ts --test` puts `\"--test\"` at index 2.",
        recap=False,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — a line at a time.
# ---------------------------------------------------------------------------

_C18_S1 = _pstep(
    "lines", "A line at a time",
    "`node:readline`, a listener per line — and the first arrow function in the project.",
    """
Everything so far has read all of stdin at once:

```ts
readFileSync(0, "utf8")
```

For a pipe that is ideal. For a person at a terminal it is useless as a REPL:
it waits until they press Ctrl+D to say the input has *ended*, and only then
evaluates. A REPL has to answer each line as it arrives.

Node's `node:readline` does that:

```ts
import { createInterface } from "node:readline";

function repl(env: Env): void {
  const rl = createInterface({ input: process.stdin });
  rl.on("line", (line) => {
    if (line.trim() === "") {
      return;
    }
    console.log(main(line.trimEnd(), env).text);
  });
}
```

`createInterface` wraps stdin in something that splits it into lines. `rl.on("line",
…)` says: *every time a line arrives, call this function with it.*

### The arrow function

```ts
(line) => {
  …
}
```

is a function with no name, written right where it is used. You have written
plenty of functions; this is the first time one is handed to someone else to
call later — a **callback**. `readline` calls it, once per line, for as long as
input keeps coming. That is why `=>` waited until module 18: nothing before
needed to give a function away.

`line` needs no type annotation. `on`'s declaration says a `"line"` listener
receives a `string`, and TypeScript fills it in.

### Every line is a program

`main(line.trimEnd(), env)` — module 17's boundary, called once per line. Each
line is scanned, parsed and run as its own program, so an error's position is
`1:C` and the caret goes under the line just typed. A blank line prints nothing,
the way every REPL behaves.
""",
    """
```
$ printf 'let x = 4\\nx * x\\ny + 1' | node calc.ts
4
16
error: undefined variable 'y' at 1:1
  y + 1
  ^
```

(In the judged version, where the REPL reads piped lines without a prompt.)
""",
    pitfalls=[
        "`readFileSync(0, \"utf8\").split(\"\\n\")` as a REPL. It gives the right output for a pipe and nothing at all for a person until they press Ctrl+D.",
        "Calling `rl.on` in a loop. It registers a listener once; `readline` does the looping.",
        "Printing inside the listener with `process.stdout` and forgetting the newline. `console.log` adds it.",
        "Annotating the parameter wrongly — `(line: number) => …`. It does not compile, because `on` says it is a string.",
    ],
    warmup=[
        _pq("Why can't the REPL use `readFileSync(0, \"utf8\")`?",
            ["It returns only when stdin ENDS — a person at a terminal would see nothing until Ctrl+D",
             "It cannot read from a terminal",
             "It returns bytes, not text",
             "It can"],
            0,
            "A REPL answers as it goes."),
    ],
    exercises=[
        _pex("calc-m18-lines-1", "Once per line",
             "Register the listener: for every line that arrives, skip it if it "
             "is blank, otherwise print what `main` makes of it.",
             _C18_REPL_FULL,
             '  rl.on("line", (line) => {',
             _C18_REPL_TESTS,
             ["`rl.on(event, listener)`.",
              "The event is `\"line\"`; the listener is an arrow function taking the line.",
              "`rl.on(\"line\", (line) => {`"]),
        _pex("calc-m18-lines-2", "A blank line is not a program",
             "Inside the listener, a line that is only whitespace prints nothing.",
             _C18_REPL_FULL,
             '    if (line.trim() === "") {\n      return;\n    }',
             _C18_REPL_TESTS,
             ["`.trim()` removes whitespace from both ends.",
              "`return` from the listener ends this line's work.",
              "`if (line.trim() === \"\") { return; }`"]),
    ],
    quiz=[
        _pq("What is a callback?",
            ["A function handed to someone else to call later — here, once per line of input",
             "A function that calls itself",
             "A function with no return value",
             "An error handler"],
            0,
            "The first one in this project, and the reason `=>` arrived now."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — an environment that outlives a line.
# ---------------------------------------------------------------------------

_C18_S2 = _pstep(
    "session", "An environment that outlives a line",
    "One `Map` for the whole session — which is why `evaluate` has taken its environment as a parameter since module 12.",
    """
```ts
repl(new Map());
```

The environment is made **once**, before the first line, and every line runs
against it:

```
> let x = 4
4
> x * x
16
```

Module 12 made the environment a parameter of `evaluate` rather than a global,
and said this is why. Module 13 made `run` take it too. Here is the payoff:
nothing in the language changes for the REPL. The same `main(src, env)` that
module 17 called with a fresh `new Map()` for a whole program is called here
with one long-lived Map, line after line.

### Errors end the line, not the session

A failure on one line prints its report, and the next line runs normally:

```
> y + 1
error: undefined variable 'y' at 1:1
  y + 1
  ^
> let y = x + 1
5
```

`main` never throws — module 17's boundary made sure of that — so one bad line
cannot take the listener down with it.

### Module 13's question, answered in public

Module 13 asked: in `let a = 1; a / 0`, is `a` bound? Statements run in order
and the first succeeded, so yes. In a single program nobody could see it. In a
REPL they can:

```
> let a = 1; a / 0
error: division by zero at 1:14
  let a = 1; a / 0
               ^
> a
1
```

That is a decision, and a defensible one — most REPLs work this way.
""",
    """
```
> let n = 10
10
> let n = n * 2
20
> n
20
```

Rebinding reads the old value first, then replaces it — across lines, exactly as
within one.
""",
    pitfalls=[
        "`main(line, new Map())` inside the listener. Every line starts with nothing defined, and `let x = 4` is forgotten immediately.",
        "A global environment instead of a parameter. It works for the REPL and breaks the test suite, which needs a fresh one per case.",
        "Letting an error end the session. A REPL is for experimenting; mistakes are the normal case.",
    ],
    warmup=[
        _pq("Where is the REPL's environment created?",
            ["Once, before the first line — passed to `repl`, and shared by every line",
             "Once per line",
             "Inside `evaluate`",
             "In the scanner"],
            0,
            "Its lifetime is the session."),
    ],
    exercises=[
        _pfix("calc-m18-session-fix1", "A REPL with no memory",
              "`let x = 4` prints `4`. The next line, `x * x`, says `x` is "
              "undefined. Every line is evaluated as if it were the first.",
              _c18_repl(_C18_REPL.replace("console.log(main(line.trimEnd(), env).text);",
                                          "console.log(main(line.trimEnd(), new Map()).text);")),
              _C18_REPL_FULL,
              _C18_REPL_TESTS,
              ["Which environment does each line run against?",
               "A new, empty one — made inside the listener.",
               "Use the environment `repl` was given: `main(line.trimEnd(), env)`."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why did the REPL need no changes to `evaluate`, `run` or `main`?",
            ["They have taken the environment as a parameter since module 12, so the caller chooses its lifetime",
             "Because the REPL reimplements them",
             "Because environments are global",
             "It needed many changes"],
            0,
            "A decision made six modules ago, paying out."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — a test runner is a loop and a comparison.
# ---------------------------------------------------------------------------

_C18_S3 = _pstep(
    "suite", "A test runner is a loop and a comparison",
    "Cases, `check`, the first differing line with `.split`, and a summary with `.map`.",
    """
Every module has had judged exercises checking `calc.ts` from outside. Your own
copy deserves tests that live *with* it, so that the next feature you add cannot
quietly break the last one. No framework — just what a framework does:

```ts
type Case = { src: string; want: string };

const CASES: Case[] = [
  { src: "1 + 2 * 3", want: "7" },
  { src: "1 + )", want: "error: unexpected ')' at 1:5\\n  1 + )\\n      ^" },
  …
];
```

A case is an input and the exact text it should produce — the error reports
included, caret and all, because the error text has been contract since module 4.

### Checking one case

```ts
function check(c: Case): boolean {
  const got = main(c.src, new Map()).text;
  if (got === c.want) {
    return true;
  }
  const gotLines = got.split("\\n");
  const wantLines = c.want.split("\\n");
  let i = 0;
  while (i < gotLines.length && i < wantLines.length && gotLines[i] === wantLines[i]) {
    i = i + 1;
  }
  console.log(`FAIL ${c.src}`);
  console.log(`  line ${i + 1}`);
  console.log(`  want: ${JSON.stringify(wantLines[i])}`);
  console.log(`  got:  ${JSON.stringify(gotLines[i])}`);
  return false;
}
```

Pass: say nothing. Fail: say which case, and — because a three-line report is
hard to compare by eye — *which line* first differs, with both versions quoted by
`JSON.stringify` so a stray space is visible. `.split("\\n")` cuts a report into
its lines.

### Running them all

```ts
const results = CASES.map((c) => check(c));
```

`.map` calls `check` on every case and collects the answers — a `boolean[]`,
one per case. Then count the `true`s and print one line:

```
12 passed, 0 failed
```

That is a test framework: cases, a runner, a comparison, a failure report, a
summary. Everything else a real one offers — setup, grouping, parallelism,
pretty output — is convenience on top of these forty lines.
""",
    """
```
$ node calc.ts --test
12 passed, 0 failed
```

Change one expected text and run it again to see a failure report.
""",
    pitfalls=[
        "Comparing only the first line of an error. The caret line is contract too; a caret in the wrong column should fail.",
        "Printing every passing case. With a hundred cases the one failure scrolls off the screen.",
        "`got == c.want` after trimming both. It hides the trailing-space bug the report is meant to show.",
        "`.map` with a function that prints and returns nothing. `results` is then an array of `undefined`, and nothing counts as passed.",
    ],
    warmup=[
        _pq("What does `CASES.map((c) => check(c))` produce?",
            ["An array of booleans — `check`'s answer for each case, in order",
             "A single boolean",
             "The number of passing cases",
             "Nothing; it only runs the checks"],
            0,
            "`map` collects what the callback returns."),
    ],
    exercises=[
        _pex("calc-m18-suite-1", "Run every case",
             "Collect a pass/fail answer for every case by calling `check` on each.",
             _C18_SUITE_FULL,
             "const results = CASES.map((c) => check(c));",
             _C18_SUITE_TESTS,
             ["An array method that calls a function on every element and collects the results.",
              "The function is an arrow taking one case.",
              "`const results = CASES.map((c) => check(c));`"]),
        _pex("calc-m18-suite-2", "Cut a report into lines",
             "In `check`, split both the actual and the expected text into lines "
             "so the first difference can be found.",
             _C18_SUITE_FULL,
             '  const gotLines = got.split("\\n");\n  const wantLines = c.want.split("\\n");',
             _C18_SUITE_TESTS,
             ["`.split` cuts a string wherever the separator appears.",
              "The separator is a newline.",
              "`const gotLines = got.split(\"\\n\"); const wantLines = c.want.split(\"\\n\");`"]),
    ],
    quiz=[
        _pq("Why does a failing case report the first differing LINE, not just \"failed\"?",
            ["Error reports are three lines; saying which line differs — quoted, so spaces show — tells you where to look",
             "Because tests must print",
             "For speed",
             "It should only say failed"],
            0,
            "A test that fails usefully is half of a test."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — tests that do not leak, and one file with three modes.
# ---------------------------------------------------------------------------

_C18_S4 = _pstep(
    "modes", "Isolated tests, and three modes",
    "Every case gets a fresh environment — and the finished `calc.ts` picks REPL, suite or program by how it was started.",
    """
### A fresh environment per case

`check` calls `main(c.src, new Map())` — a **new** environment for every case.
It looks wasteful. Share one instead and watch what happens:

```
{ src: "let x = 4; x * x", want: "16" },
{ src: "x", want: "error: undefined variable 'x' at 1:1\\n  x\\n  ^" },
```

With a shared environment, the first case leaves `x` bound, and the second —
which is testing that an undefined name is reported — finds it defined and prints
`4`. The second case fails because of the first. Reorder them and it passes.

Tests that depend on each other's leftovers are the most expensive kind of bug a
suite can have: they fail in ways that have nothing to do with the code under
test, and they change when you add or reorder cases. **Every test starts from
nothing.** It is the same lifetime question as the REPL, answered the other way:
the REPL wants one environment for the session; a suite wants one per case. The
environment has been a parameter since module 12, so both are one argument away.

### One file, three modes

The finished `calc.ts` decides what to do from how it was started:

```ts
if (process.argv[2] === "--test") {
  runTests();
} else if (process.stdin.isTTY) {
  repl(new Map());
} else {
  const outcome = main(readFileSync(0, "utf8").trimEnd(), new Map());
  …
  process.exitCode = outcome.code;
}
```

| Started as | Mode |
|---|---|
| `node calc.ts --test` | run the suite; exit 1 if anything failed |
| `node calc.ts` at a terminal | the REPL, with a `> ` prompt |
| `echo '1 + 2' \\| node calc.ts` | one whole program, as in module 17 |

`process.stdin.isTTY` is true when stdin is a terminal a person is typing into,
and not when something is piped in — which is exactly the difference between
"someone wants to experiment" and "a script wants an answer".
""",
    """
```bash
$ node calc.ts --test
12 passed, 0 failed
$ echo 'let x = 4; x * x' | node calc.ts
16
$ node calc.ts
> 2 < 3
true
```

The project's `manual_test`, in full, now works.
""",
    pitfalls=[
        "One environment shared by every test case. Cases start depending on each other's `let`s, and a suite passes or fails depending on order.",
        "The REPL on piped input. A script piping a file in would get one answer per LINE instead of one for the program — `isTTY` is how to tell.",
        "`--test` exiting 0 when a case fails. A suite that cannot fail a build is a suite nobody runs.",
    ],
    warmup=[
        _pq("Why does each test case get `new Map()`?",
            ["So no case can see another's bindings — every test starts from nothing and order cannot matter",
             "Because Maps cannot be reused",
             "For speed",
             "It should share one"],
            0,
            "Isolation is the first rule of a test suite."),
    ],
    exercises=[
        _pfix("calc-m18-modes-fix1", "A test that fails because of another test",
              "The suite reports `11 passed, 1 failed`: the case `x` expected "
              "`undefined variable 'x'` and got `4`. Run that case on its own and "
              "it passes.",
              _c18_suite(check="const shared: Env = new Map();\n\n" +
                         _C18_CHECK.replace("main(c.src, new Map())", "main(c.src, shared)")),
              _C18_SUITE_FULL,
              _C18_SUITE_TESTS,
              ["Where did `x` get the value 4?",
               "An earlier case bound it, in an environment every case shares.",
               "Give every case its own: `main(c.src, new Map())` — and delete the shared one."],
              difficulty="Medium"),
        _pex("calc-m18-modes-1", "Count the passes",
             "After collecting the results, count the passes and print the "
             "summary line.",
             _C18_SUITE_FULL,
             "for (const ok of results) {\n  if (ok) {\n    passed = passed + 1;\n  }\n}\nconsole.log(`${passed} passed, ${results.length - passed} failed`);",
             _C18_SUITE_TESTS,
             ["Loop over `results`; each is a boolean.",
              "Failures are the total minus the passes.",
              "`console.log(`${passed} passed, ${results.length - passed} failed`);`"]),
    ],
    quiz=[
        _pq("The REPL shares one environment; the suite gives each case its own. Why is that consistent?",
            ["The environment's lifetime is the caller's choice — a session for the REPL, a case for a test — and it has been a parameter since module 12",
             "It is not consistent",
             "Because tests are faster",
             "Because the REPL is special"],
            0,
            "Same function, different lifetimes."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C18_FINAL = _pch(
    "calc-m18-build", "Module 18 build — the finished pipeline, interactive", "Hard",
    "Write the last layer of `calc.ts`, from `run` to the end:\n\n"
    "* `Outcome` and `run` — scan, parse, run; a report with code 1 at the first "
    "failure, or the value with code 0\n"
    "* `main` — one `try` at the edge; anything thrown is `error: internal error: "
    "<message>` with code 2\n"
    "* `repl` — a line reader over stdin; blank lines skipped; every other line "
    "run by `main` against ONE environment, its text printed\n"
    "* the call that starts the REPL with an empty environment\n\n"
    "The tests are whole sessions: definitions on one line are used on the next, "
    "and errors do not end the session.",
    _C18_REPL_FULL,
    _cjoin(_C17_RUN, _C17_BOUNDARY, _C18_REPL).rstrip("\n"),
    _C18_REPL_TESTS,
    ["`run` and `main` are module 17's.",
     "`repl`: `createInterface({ input: process.stdin })`, then `rl.on(\"line\", (line) => { … })`.",
     "Skip `line.trim() === \"\"`; otherwise `console.log(main(line.trimEnd(), env).text)`.",
     "`repl(new Map());` — one environment, made once."],
)


_CALC_MODULES.append(_pmod(
    key="calc-repl", number=18, phase="usable",
    title="A REPL, and a test suite you wrote",
    what="read stdin line by line, and prove the whole thing with no framework",
    goal="Leave the language in a shape you would be happy to add a feature to.",
    why=_C18_WHY,
    est_minutes=50,
    builds_on=["calc-vars", "calc-statements", "calc-messages"],
    concepts=["REPL", "readline", "callbacks", "arrow functions", "environment lifetime",
              "test runners", "test isolation", "split and map", "program modes"],
    deliverable="The finished language: `node calc.ts` is an interactive REPL that "
                "remembers between lines, `node calc.ts --test` runs a suite you "
                "wrote, and piped input is still one program with an exit code.",
    objectives=[
        "Explain why `readFileSync` cannot drive a REPL, and read stdin a line at a time instead",
        "Write an arrow function as a callback, and say why `=>` waited for this module",
        "Choose an environment's lifetime — one per session, one per test — and say why both work unchanged",
        "Write a test runner with cases, a comparison, a first-difference report and a summary",
        "Explain test isolation and show the bug a shared environment causes",
        "Pick a program's mode from its arguments and whether stdin is a terminal",
    ],
    brief=_C18_BRIEF,
    syntax=_C18_SYNTAX,
    steps=[_C18_S1, _C18_S2, _C18_S3, _C18_S4],
    final_build=_C18_FINAL,
    acceptance=[
        "`node calc.ts` at a terminal shows a `> ` prompt, and `let x = 4` then `x * x` prints `4` then `16`.",
        "An error in the REPL prints its report with a caret and the session carries on.",
        "Blank lines in the REPL print nothing.",
        "`node calc.ts --test` prints `N passed, 0 failed` and exits 0; breaking one expected text makes it report the case, the line, and exit 1.",
        "Every test case runs against a fresh environment.",
        "`echo 'let x = 4; x * x' | node calc.ts` still prints `16` — piped input is one program.",
        "Everything in the project's acceptance list at the top of Calc passes.",
    ],
    manual_test="""
```bash
node calc.ts --test                     # 12 passed, 0 failed  (and exit 0)
echo 'let x = 4; x * x' | node calc.ts  # 16 — piped input is still one program
node calc.ts                            # the REPL
```

In the REPL:

```
> let x = 4
4
> x * x > 10
true
> if x > 3 then x * 2 else 0
8
> y + 1
error: undefined variable 'y' at 1:1
  y + 1
  ^
> let a = 1; a / 0
error: division by zero at 1:14 …
> a
1
```

Press Ctrl+D (Ctrl+Z then Enter on Windows) to leave.

Then use the suite the way it is meant to be used. Add a feature from the stretch
list — `%` is the smallest — and add its cases to `CASES` before writing the code.
Run `--test`: the new cases fail, the old ones pass. Write the feature. Run it
again. That loop is what the last eighteen modules were building towards.
""",
    reference="""// calc.ts — module 18: the finished language.
//
//   text → scan → tokens → parse → program → run → value
//
// A scanner, a recursive-descent parser, an evaluator over a discriminated-union
// tree, errors as values with positions and carets, one try/catch at the edge,
// and exit codes a script can use. Three modes:
//
//   node calc.ts --test          run the suite below (exit 1 on any failure)
//   node calc.ts                 a REPL, one environment for the whole session
//   echo '…' | node calc.ts      one program, as a script would use it
""" + _C18_REFERENCE,
    stretch=[
        "Add `%`, `<=`, `>=` and `!=` test-first: write the cases, watch them fail, make them pass. Count the files you touched (one) and the functions the compiler sent you to.",
        "Add functions: `fn double(n) = n * 2; double(21)`. You need a call expression, an environment that can nest (a function's parameters shadow the outer names), and an error for the wrong number of arguments. This is the biggest stretch, and it is how every real language grows up.",
        "Write a formatter: parse a program and print it back with canonical spacing and only the brackets precedence requires. Add a `--format` mode. It reuses the whole front end and none of the evaluator.",
        "Make the REPL accept a program over several lines: if a line ends in the middle of an expression (the parser reports `unexpected end of input`), keep reading and try again with the next line appended.",
        "Split `calc.ts` into files — `scan.ts`, `parse.ts`, `evaluate.ts`, `main.ts` — with `export` and `import`. Notice which types each file needs from the others; that list is the architecture.",
    ],
    glossary=[
        _pgloss("REPL", "Read-eval-print loop: read a line, evaluate it, print the result, repeat — with state kept between lines."),
        _pgloss("readline", "Node's built-in line reader. It calls a listener once per line of input."),
        _pgloss("callback", "A function handed to other code to be called later. `rl.on(\"line\", (line) => …)`."),
        _pgloss("arrow function", "`(x) => { … }` — a function written inline, without a name."),
        _pgloss("test runner", "Code that runs a list of cases, compares results with expectations, and reports failures and a summary."),
        _pgloss("test isolation", "Each test starting from a clean state, so no test's result depends on another's."),
        _pgloss("TTY", "A terminal a person is typing into. `process.stdin.isTTY` tells an interactive session from piped input."),
    ],
    cheatsheet="""
```ts
import { createInterface } from "node:readline";

function repl(env: Env): void {                         // ONE env for the session
  const rl = createInterface({ input: process.stdin });
  rl.on("line", (line) => {                             // a callback, per line
    if (line.trim() === "") { return; }
    console.log(main(line.trimEnd(), env).text);
  });
}

function check(c: Case): boolean {
  const got = main(c.src, new Map()).text;              // a FRESH env per case
  if (got === c.want) { return true; }
  const gotLines = got.split("\\n");                     // find the first differing line
  …
}
const results = CASES.map((c) => check(c));

if (process.argv[2] === "--test") { runTests(); }
else if (process.stdin.isTTY) { repl(new Map()); }
else { /* one program, module 17 */ }
```

| Started as | Mode |
|---|---|
| `node calc.ts --test` | the suite |
| `node calc.ts` | the REPL |
| `… \\| node calc.ts` | one program |

| Symptom | Cause |
|---|---|
| REPL forgets `let` between lines | a new Map per line |
| a test fails only after another | environment shared between cases |
| the REPL waits for Ctrl+D | `readFileSync` instead of `readline` |
""",
    self_check=[
        "Can you explain why a REPL needs `readline` and a pipe does not?",
        "Can you write an arrow-function listener and say where its parameter's type comes from?",
        "Can you say what lifetime the environment has in the REPL, in the suite, and in whole-program mode?",
        "Can you write a test runner from memory, including the first-difference report?",
        "Can you show the bug a shared test environment causes, with two cases?",
        "Can you explain how `calc.ts` decides which mode to run in?",
    ],
    review=[
        _pq("What does `rl.on(\"line\", (line) => { … })` do?",
            ["Registers a function that readline calls once for every line of input",
             "Reads one line and returns it",
             "Loops over all lines immediately",
             "Prints a prompt"],
            0,
            "A callback — the first in the project."),
        _pq("In the REPL, `let x = 4` then `x * x`. Why does the second line see `x`?",
            ["Every line runs against the same environment, created once for the session",
             "Because the REPL re-runs every previous line",
             "Because `x` is global",
             "It does not"],
            0,
            "A long-lived environment, passed as a parameter."),
        _pq("Why does each test case get a new environment?",
            ["So no case depends on bindings another case left behind",
             "Maps cannot be reused",
             "The REPL needs the shared one",
             "It does not"],
            0,
            "Isolation: order must not matter."),
        _pq("What does `CASES.map((c) => check(c))` return?",
            ["An array of booleans, one per case",
             "The number of passes",
             "Nothing",
             "The first failure"],
            0,
            "`map` collects the callback's results."),
        _pq("How does the finished `calc.ts` know to start the REPL?",
            ["`process.stdin.isTTY` is true — a person at a terminal, not piped input",
             "A `--repl` flag is required",
             "It always starts the REPL",
             "It checks the file name"],
            0,
            "Experimenting person vs script, told apart by the stream."),
    ],
    milestone="Calc is finished — a language with a scanner, a recursive-descent "
              "parser, an evaluator over a discriminated-union tree, errors a "
              "stranger can act on, a REPL, and a test suite you wrote with no "
              "framework. Every compiler, linter, formatter and query parser you "
              "open from now on is this program with more cases in it.",
))
