# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 17 — Error messages that point at the problem.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Builds on module 16's program.
#
# TWO SUBJECTS, ONE ARGUMENT.
#
#   1. THE CARET. Module 16 made positions data; this module uses them. An error
#      report is three lines — the message, the source line it happened on, and
#      a `^` under the column:
#
#          error: unexpected ')' at 1:5
#            1 + )
#                ^
#
#      `.repeat(` is gated here for the spaces. The line is found with the
#      two-argument `indexOf` (`.split(` is module 18's).
#
#   2. throw / try / catch — THE ONLY PLACE THEY APPEAR. The module's argument is
#      a comparison, with a reason for each side:
#        * the USER's mistakes are expected → values, all the way out (as since
#          module 4), reported with a caret, exit code 1;
#        * the PROGRAM's impossibilities are unexpected → `throw`, caught ONCE at
#          the edge, reported as `error: internal error: …`, exit code 2.
#      `assertNever(x: never): never` replaces module 10's two-line default, and
#      `peek`'s fallback throws instead of inventing a `{ line: 0 }` eof (module
#      16 promised this). The catch is exercised by a real exception the program
#      never threw: ten thousand nested brackets overflow the call stack, and V8
#      throws a RangeError. Graded — `calc-m17-edge-fix1` has no boundary, and
#      crashes.
#
# EXIT CODES. 0 for a value, 1 for a user error, 2 for an internal one. A judged
# program must exit 0 and is compared on stdout, so the judged `main` prints the
# code as a last line, `exit 1`. The reference — the learner's real calc.ts —
# writes errors with `console.error` and sets `process.exitCode`, which is the
# point. `instanceof`, `console.error(` and `process.exitCode` are gated here.
# ---------------------------------------------------------------------------

_C17_NEVER_FN = """function assertNever(x: never): never {
  throw new Error(`unhandled case: ${JSON.stringify(x)}`);
}
"""


def _c17_defaults(src):
    """Module 10's two-line `never` default → a call to `assertNever`."""
    out = src
    for var in ("t", "e", "op", "s"):
        out = out.replace(
            f"    default: {{\n      const impossible: never = {var};\n      return impossible;\n    }}\n",
            f"    default:\n      return assertNever({var});\n")
    assert "impossible" not in out, out
    return out


_C17_STATE = _C16_STATE.replace("    return eofToken({ line: 0, col: 0 });",
                                '    throw new Error("peek past the end of the tokens");', 1)

_C17_REPORT = """function lineOf(src: string, line: number): string {
  let start = 0;
  let n = 1;
  while (n < line) {
    start = src.indexOf("\\n", start) + 1;
    n = n + 1;
  }
  let end = src.indexOf("\\n", start);
  if (end === -1) {
    end = src.length;
  }
  return src.slice(start, end).trimEnd();
}

function report(src: string, err: CalcError): string {
  const caret = " ".repeat(err.pos.col - 1) + "^";
  return `${formatError(err)}\\n  ${lineOf(src, err.pos.line)}\\n  ${caret}`;
}
"""

_C17_RUN = """type Outcome = { text: string; code: number };

function run(src: string, env: Env): Outcome {
  const scanned = scan(src);
  if (!scanned.ok) {
    return { text: report(src, scanned.error), code: 1 };
  }
  const parsed = parseProgram(scanned.tokens);
  if (!parsed.ok) {
    return { text: report(src, parsed.error), code: 1 };
  }
  const result = runProgram(parsed.program, env);
  if (!result.ok) {
    return { text: report(src, result.error), code: 1 };
  }
  return { text: `${result.value}`, code: 0 };
}
"""

_C17_BOUNDARY = """function main(src: string, env: Env): Outcome {
  try {
    return run(src, env);
  } catch (e) {
    let detail = "unknown";
    if (e instanceof Error) {
      detail = e.message;
    }
    return { text: `error: internal error: ${detail}`, code: 2 };
  }
}
"""

_C17_MAIN = """const outcome = main(readFileSync(0, "utf8").trimEnd(), new Map());
console.log(outcome.text);
console.log(`exit ${outcome.code}`);
"""

_C17_REAL_MAIN = """const outcome = main(readFileSync(0, "utf8").trimEnd(), new Map());
if (outcome.code === 0) {
  console.log(outcome.text);
} else {
  console.error(outcome.text);
}
process.exitCode = outcome.code;
"""


def _c17(state=_C17_STATE, report=_C17_REPORT, run=_C17_RUN, boundary=_C17_BOUNDARY,
         main=_C17_MAIN, never=_C17_NEVER_FN):
    return _stdin(_cjoin(
        _C16_TOKENS, _C16_ERRORS, never, _C16_SCAN, _C16_TREE, _C13_STMTS, state,
        _c17_defaults(_C16_DESCRIBE), _C16_PRIMARY, _C16_UNARY, _C16_PRODUCT, _C16_SUM,
        _C16_COMPARISON, _C13_PARSE_STMT, _C13_PARSE_PROGRAM, _C16_RESULT, _C14_ENV,
        _c17_defaults(_C16_EVAL), _c17_defaults(_C16_APPLY), _c17_defaults(_C16_EXECUTE),
        report, run, boundary, main))


_C17_FULL = _c17()

_C17_DEEP = "(" * 10000 + "1" + ")" * 10000
_C17_INPUTS = ["1 + )", "1 $ 2", "  1 $ 2", "1 +", "(1 + 2", "",
               "let x = 4;\nx * y", "let a = 1;\nlet b = 0;\na / b", "1 + 2 / 0",
               "if 1 then 2 else 3", "1 + 2 * 3", "let x = 4; x * x > 10",
               "let x = 1;\r\nx + 1", _C17_DEEP]
_C17_TESTS = _ctests(17, _C17_INPUTS)
_C17_SHALLOW = _ctests(17, _C17_INPUTS[:-1])

# --- Step 2's plain program: the function that cannot return -----------------
_C17_S2_MAIN = """type Shape = { kind: "dot" } | { kind: "line"; length: number };

function describeShape(s: Shape): string {
  switch (s.kind) {
    case "dot":
      return "a dot";
    case "line":
      return `a line of ${s.length}`;
    default:
      return assertNever(s);
  }
}

function at(xs: number[], i: number): number {
  const x = xs[i];
  if (x === undefined) {
    throw new Error(`no element ${i}`);
  }
  return x;
}

console.log(describeShape({ kind: "dot" }));
console.log(describeShape({ kind: "line", length: 3 }));
console.log(at([10, 20, 30], 1));
try {
  console.log(at([10, 20, 30], 5));
} catch (e) {
  if (e instanceof Error) {
    console.log(e.message);
  }
}
"""
_C17_S2_OUT = "a dot\na line of 3\n20\nno element 5"

_C17_WHY = (
    "`error: unexpected ')' at 2:14` is correct, and it still makes someone count "
    "to fourteen. Every tool people like to use shows the line and puts a mark "
    "under the problem — so this module does that, with the positions module 16 "
    "made into data. It also settles the last open question about failure. Since "
    "module 4, every error has been a returned value, and `throw` has been "
    "deliberately absent. Some failures are not the user's fault, though: a "
    "switch reaching a case that cannot exist, or JavaScript itself giving up on "
    "a ten-thousand-deep expression. Those are exceptions, and a program needs "
    "exactly one place that catches them — at its edge, with an exit code a "
    "script can read."
)

_C17_BRIEF = """
### The whole module in one line

Every error prints the line it happened on with a `^` under the column, bugs
are caught once at the edge instead of crashing, and the exit code says which
kind of failure it was.

### The caret

```
$ echo '1 + )' | node calc.ts
error: unexpected ')' at 1:5
  1 + )
      ^
```

Three lines: module 16's message, the source line, and a caret under the
column. Nothing about it is clever — find the line, print it, print `col - 1`
spaces and a `^` — and it is the single biggest difference between a tool that
reports errors and one that helps.

### Two kinds of failure

| | The user's mistake | A bug in `calc.ts` |
|---|---|---|
| Example | `1 + )`, `1 / 0`, `y + 1` | a switch reaching a case that cannot exist |
| Expected? | yes — it is why the tool exists | no |
| Travels as | a returned value, since module 4 | a thrown exception |
| Reported as | the message and a caret | `error: internal error: …` |
| Exit code | 1 | 2 |

Values for the first, because every caller must decide what to do about them
and the compiler holds them to it. Exceptions for the second, because no caller
can do anything useful about a bug except stop — and one `try`, at the very edge
of the program, is enough to make stopping clean.

### `throw` arrives — once

```ts
function assertNever(x: never): never {
  throw new Error(`unhandled case: ${JSON.stringify(x)}`);
}
```

Module 10's four-line default becomes `default: return assertNever(e);`. And
`peek`'s impossible branch, which module 16 made invent a position for a token
that cannot exist, simply throws.

### The exception you did not throw

```
$ node -e 'console.log("(".repeat(10000) + "1" + ")".repeat(10000))' | node calc.ts
error: internal error: Maximum call stack size exceeded
```

Ten thousand nested brackets are ten thousand nested calls to the parser, and
JavaScript runs out of stack. Without a boundary, that is a stack trace. With
one, it is a message and exit code 2.

### Exit codes

`0` — here is a value. `1` — your program has a mistake. `2` — calc has one.
A script piping into `calc.ts` can finally tell them apart.
"""

_C17_SYNTAX = [
    _syn(
        "\" \".repeat(err.pos.col - 1) + \"^\"",
        "`s.repeat(n)` is `s` written `n` times — here, enough spaces to move the "
        "caret under the right column.",
        """
" ".repeat(4) + "^"      // "    ^"
" ".repeat(0) + "^"      // "^"  — column 1
""",
        "`col - 1` spaces, because the caret itself occupies the column.",
    ),
    _syn(
        "src.indexOf(\"\\n\", start)",
        "`indexOf` with a second argument starts searching from that index — so "
        "repeated calls walk from one line break to the next.",
        "",
        "It still returns `-1` when there is nothing more to find: the last line "
        "has no `\\n` after it.",
    ),
    _syn(
        "throw new Error(`unhandled case: ${JSON.stringify(x)}`);",
        "Stop the current function — and every caller above it — with an "
        "exception, until something catches it.",
        "",
        "Used in exactly two places: code the type system says cannot run. Every "
        "failure the USER can cause stays a returned value.",
    ),
    _syn(
        "function assertNever(x: never): never { … }",
        "A function whose return type is `never` — it cannot return at all, "
        "because it always throws. Calling it satisfies any return type.",
        """
default:
  return assertNever(e);    // compiles only if e is never — module 10's check
""",
        "The parameter type does module 10's job (a forgotten case is still a "
        "compile error); the body does module 17's (if it somehow runs, it says so).",
    ),
    _syn(
        "try { return run(src, env); } catch (e) { … }",
        "Run the `try` block; if anything inside it — at any depth — throws, "
        "jump to `catch` with what was thrown.",
        "",
        "`e` has type `unknown`: anything can be thrown, not only `Error`s. It "
        "has to be checked before it is used.",
    ),
    _syn(
        "if (e instanceof Error) { detail = e.message; }",
        "`x instanceof C` is true when `x` was made by `new C(…)`. It narrows an "
        "`unknown` to that class, so `.message` becomes readable.",
        "",
        "",
    ),
    _syn(
        "console.error(outcome.text);",
        "Write to **stderr** instead of stdout. Errors go there, so a script "
        "capturing a program's output does not capture its complaints.",
        "",
        "In the judged exercises everything goes to stdout, so it can be compared. "
        "Your own `calc.ts` uses this.",
    ),
    _syn(
        "process.exitCode = outcome.code;",
        "Set the number the process reports to the shell when it ends: 0 for "
        "success, anything else for failure.",
        "",
        "Setting `exitCode` lets the program finish normally; `echo $?` in a "
        "shell shows it afterwards.",
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — show the line, point at the column.
# ---------------------------------------------------------------------------

_C17_S1 = _pstep(
    "caret", "Show the line, point at the column",
    "`lineOf` finds the source line; `report` prints the message, the line, and a caret.",
    """
Module 16 made an error a message and a position. Printing that position as
`at 2:14` makes the reader do the finding. Do it for them:

```
error: undefined variable 'y' at 2:5
  x * y
      ^
```

Two things are needed: the text of line 2, and a caret under column 5.

### Finding a line

```ts
function lineOf(src: string, line: number): string {
  let start = 0;
  let n = 1;
  while (n < line) {
    start = src.indexOf("\\n", start) + 1;
    n = n + 1;
  }
  let end = src.indexOf("\\n", start);
  if (end === -1) {
    end = src.length;
  }
  return src.slice(start, end).trimEnd();
}
```

Hop from line break to line break until you are at the right line —
`indexOf("\\n", start)` finds the next break at or after `start`, and the line
begins just past it. Then cut up to the next break, or to the end of the source
for the last line. `.trimEnd()` removes a `\\r` from a Windows line ending, so it
does not end up printed.

### The caret

```ts
function report(src: string, err: CalcError): string {
  const caret = " ".repeat(err.pos.col - 1) + "^";
  return `${formatError(err)}\\n  ${lineOf(src, err.pos.line)}\\n  ${caret}`;
}
```

`col - 1` spaces, then the caret: column 1 gets no spaces, and the caret sits
*on* the column rather than after it. Both the line and the caret are indented by
the same two spaces, so they stay aligned.

At the end of the input — `1 +` — the column is one past the last character, and
the caret lands just after the `+`: exactly where the missing operand should have
been.
""",
    """
```
$ echo '1 + )' | node calc.ts
error: unexpected ')' at 1:5
  1 + )
      ^
$ echo '1 +' | node calc.ts
error: unexpected end of input at 1:4
  1 +
     ^
```
""",
    pitfalls=[
        "`\" \".repeat(err.pos.col)` — the caret is one column to the right of every mistake.",
        "Indenting the line but not the caret, or the other way round. They must be offset by the same amount or the caret points at the wrong character.",
        "Printing the whole source instead of the line. For a one-line program it looks the same; for a fifty-line one it buries the error.",
        "Leaving a `\\r` on the printed line. Some terminals then return the cursor to the start and print the caret line over it.",
    ],
    warmup=[
        _pq("An error is at column 1. How many spaces go before the caret (not counting the indent)?",
            ["0 — `col - 1` spaces, so the caret sits on the first column",
             "1",
             "2",
             "It depends on the line"],
            0,
            "The caret occupies its column."),
    ],
    exercises=[
        _pex("calc-m17-caret-1", "Under the column",
             "Build the caret line: enough spaces to reach the error's column, "
             "then a `^`.",
             _C17_FULL,
             '  const caret = " ".repeat(err.pos.col - 1) + "^";',
             _C17_SHALLOW,
             ["`\" \".repeat(n)` is `n` spaces.",
              "The caret itself takes up the column — how many spaces come before it?",
              "`const caret = \" \".repeat(err.pos.col - 1) + \"^\";`"]),
        _pfix("calc-m17-caret-fix1", "One to the right",
              "Every caret lands one character to the right of the mistake. In "
              "`1 + )` it points past the `)`, at nothing.",
              _c17(report=_C17_REPORT.replace('" ".repeat(err.pos.col - 1)', '" ".repeat(err.pos.col)')),
              _C17_FULL,
              _C17_SHALLOW,
              ["Columns count from 1. How many spaces does column 1 need?",
               "The caret occupies its own column.",
               "`\" \".repeat(err.pos.col - 1)`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why is `.trimEnd()` applied to the line before printing it?",
            ["A Windows line ends in `\\r`, which would be printed and can garble the caret line",
             "To remove the error",
             "Because lines have trailing tokens",
             "It is not needed"],
            0,
            "The source can have line endings from anywhere."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — two kinds of failure.
# ---------------------------------------------------------------------------

_C17_S2 = _pstep(
    "throw", "Two kinds of failure",
    "User mistakes stay values. Impossibilities throw — and `assertNever` is where.",
    """
Since module 4, this project has kept one rule: **a failure is a value**. The
scanner returns one, the parser returns one, the evaluator returns one, and
every caller is made by the compiler to deal with it. That rule stays. Every
mistake a *user* can make is still a returned value.

But there is a second kind of failure, and it has been hiding in two places.

### Things that cannot happen

`peek`'s fallback, for a cursor past the end of the tokens — which cannot happen,
because `advance` stops at `eof`. Module 16 had to invent `{ line: 0, col: 0 }`
for it.

And module 10's default:

```ts
default: {
  const impossible: never = e;
  return impossible;
}
```

— which also cannot run: the compiler proved every case is handled.

If either of these ever *does* run, it is not the user's fault. It is a bug in
`calc.ts`. There is nothing the caller can do about it — no message to show the
user that helps them fix their program — and returning a value would force every
caller to handle a failure that is not supposed to exist.

### `throw`

That is what exceptions are for:

```ts
function assertNever(x: never): never {
  throw new Error(`unhandled case: ${JSON.stringify(x)}`);
}
```

The parameter type does module 10's job: `assertNever(e)` only compiles when `e`
is `never`. The body does this module's: if it runs anyway — say, a value from
outside the type system got in — it stops with a message naming what it got. The
return type `never` means "this function does not return", so `return
assertNever(e);` satisfies any function.

Every switch's default becomes one line:

```ts
default:
  return assertNever(e);
```

and `peek` throws instead of lying:

```ts
if (t === undefined) {
  throw new Error("peek past the end of the tokens");
}
```

### The rule

> A failure the user can cause is a **value**. A failure only a bug can cause is
> an **exception**.
""",
    """
```
a dot
a line of 3
20
no element 5
```

`describeShape` compiles because `assertNever` sees `never` in its default. `at`
is `peek` in miniature: asking for an element that is not there is the caller's
bug, so it throws — and the `catch` shows the message.
""",
    pitfalls=[
        "Throwing for user mistakes. `1 / 0` would stop being something the compiler makes every caller handle.",
        "`assertNever(x: never): void`. Then `return assertNever(e)` does not satisfy a function that returns a value.",
        "Throwing a string: `throw \"unhandled\"`. It works, and a caught string has no `.message` — `instanceof Error` is false.",
        "Keeping module 10's `return impossible;` AND adding `assertNever`. One line does both jobs now.",
    ],
    warmup=[
        _pq("Should `1 / 0` throw now that `throw` is available?",
            ["No — it is the user's mistake, so it stays a returned value that every caller must handle",
             "Yes — errors should throw",
             "Only in the evaluator",
             "Only when the divisor is a literal"],
            0,
            "Exceptions are for impossibilities, not for input."),
    ],
    exercises=[
        _pex("calc-m17-throw-1", "A function that cannot return",
             "Finish `assertNever`: stop with an `Error` whose message is "
             "`unhandled case: ` and the value as JSON.",
             _plain(_cjoin(_C17_NEVER_FN, _C17_S2_MAIN)),
             "  throw new Error(`unhandled case: ${JSON.stringify(x)}`);",
             [("", _C17_S2_OUT)],
             ["`throw new Error(message)`.",
              "`JSON.stringify(x)` turns the unexpected value into text.",
              "`throw new Error(`unhandled case: ${JSON.stringify(x)}`);`"]),
        _pex("calc-m17-throw-2", "Asking for what is not there",
             "Finish `at`: an index past the end is the caller's bug, not a "
             "value — throw an `Error` saying `no element <i>`.",
             _plain(_cjoin(_C17_NEVER_FN, _C17_S2_MAIN)),
             "    throw new Error(`no element ${i}`);",
             [("", _C17_S2_OUT)],
             ["`peek`'s situation, in miniature.",
              "`throw new Error(…)` with a template literal.",
              "`throw new Error(`no element ${i}`);`"]),
    ],
    quiz=[
        _pq("Why may `assertNever` be declared to return `never`?",
            ["It always throws, so it never returns — and `never` is assignable to every return type",
             "Because it returns undefined",
             "Because `never` means optional",
             "It returns `x`"],
            0,
            "`return assertNever(e)` then fits in any function."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — one try, at the edge.
# ---------------------------------------------------------------------------

_C17_S3 = _pstep(
    "edge", "One `try`, at the edge",
    "The boundary that turns any exception into a clean message — including one JavaScript threw for you.",
    """
Exceptions travel up through every caller until something catches them. So there
needs to be exactly one place that does, and it belongs at the outermost edge of
the program:

```ts
function main(src: string, env: Env): Outcome {
  try {
    return run(src, env);
  } catch (e) {
    let detail = "unknown";
    if (e instanceof Error) {
      detail = e.message;
    }
    return { text: `error: internal error: ${detail}`, code: 2 };
  }
}
```

One `try`. Not one per function, not one around each stage — one, wrapping
everything, with values everywhere inside it. That is the design the whole
project was built towards: **results as values inside, one catch outside.**

### `e` is `unknown`

Anything can be thrown in JavaScript — an `Error`, a string, a number. So the
caught value has type `unknown`, and nothing can be read from it until it has
been narrowed. `instanceof Error` narrows it to an `Error`, whose `.message` is
readable.

### The exception you did not throw

`assertNever` and `peek` should never throw. Here is one that will:

```
((((((((((…ten thousand of them…1))))))))))
```

Each `(` is a call to `parseExpr`, which calls `parseComparison`, which calls
`parseSum`… six calls per bracket, sixty thousand deep. JavaScript's call stack
is not that deep, and it gives up:

```
RangeError: Maximum call stack size exceeded
```

`calc.ts` never wrote `throw` for this. The runtime did. Without the boundary,
the user gets a stack trace and a crash; with it, they get:

```
error: internal error: Maximum call stack size exceeded
```

It is still not a *good* message — the stretch list has a proper depth limit —
but it is clean, it is one line, and the program ends on its own terms.
""",
    """
```bash
$ node -e 'console.log("(".repeat(10000) + "1" + ")".repeat(10000))' | node calc.ts
error: internal error: Maximum call stack size exceeded
```

One line, no stack trace.
""",
    pitfalls=[
        "A `try` in every function. It hides where the exception came from and makes a bug look like a handled case.",
        "`catch (e) { return { text: e.message, … } }` — `e` is `unknown`, and it does not compile until narrowed.",
        "Catching and continuing as if nothing happened. The program is in a state its author said was impossible; stopping is the only honest move.",
        "Printing the stack trace to the user. It is written for the programmer — useful in a log, noise in a message.",
    ],
    warmup=[
        _pq("Why is `e` in `catch (e)` of type `unknown`?",
            ["JavaScript can throw any value, not only `Error`s",
             "Because the error has no type",
             "Because `catch` is untyped",
             "It is `Error`"],
            0,
            "Narrow before reading."),
    ],
    exercises=[
        _pfix("calc-m17-edge-fix1", "Ten thousand brackets",
              "Every ordinary input works. Ten thousand nested brackets crash the "
              "program with a `RangeError` and a stack trace, and nothing is "
              "printed on stdout at all.",
              _c17(boundary="""function main(src: string, env: Env): Outcome {
  return run(src, env);
}
"""),
              _C17_FULL,
              _C17_TESTS,
              ["Where would an exception from anywhere in `run` be caught?",
               "Nowhere — there is no boundary.",
               "Wrap `run` in `try`; in `catch`, narrow with `instanceof Error` and return an internal error with code 2."],
              difficulty="Medium"),
        _pex("calc-m17-edge-1", "Read the message safely",
             "In the boundary's `catch`, take the message from the caught value — "
             "if it is an `Error`.",
             _C17_FULL,
             "    if (e instanceof Error) {\n      detail = e.message;\n    }",
             _C17_TESTS,
             ["`e` is `unknown` — narrow it first.",
              "`instanceof Error` is the check.",
              "`if (e instanceof Error) { detail = e.message; }`"]),
    ],
    quiz=[
        _pq("How many `try` blocks does `calc.ts` have, and why that many?",
            ["One, at the edge — every expected failure is a value inside, and exceptions are only for bugs",
             "One per stage",
             "One per function",
             "None"],
            0,
            "Results inside, one catch outside."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — exit codes, and stderr.
# ---------------------------------------------------------------------------

_C17_S4 = _pstep(
    "exit", "Exit codes, and where errors go",
    "`Outcome`: text and a code — 0, 1 or 2 — and the two lines that send it to a shell.",
    """
Since module 4 the error message has gone to stdout "for now", and the program
has exited 0 whatever happened. Module 4 promised this decision, for every kind
of error at once. Here it is.

```ts
type Outcome = { text: string; code: number };
```

`run` returns one: the value with code **0**, or the report with code **1**.
The boundary returns code **2**. Three codes, three meanings:

| Code | Meaning | Who should act |
|---|---|---|
| 0 | here is the value | nobody |
| 1 | the program you gave me has a mistake | the user |
| 2 | calc itself went wrong | whoever maintains calc |

### Your `calc.ts`

```ts
const outcome = main(readFileSync(0, "utf8").trimEnd(), new Map());
if (outcome.code === 0) {
  console.log(outcome.text);
} else {
  console.error(outcome.text);
}
process.exitCode = outcome.code;
```

Values go to **stdout**, errors to **stderr**, and the exit code tells a script
which happened without it having to read either. `calc.ts '…' > answer.txt`
stays clean when something fails, and `if node calc.ts < prog; then …` works.

### The judged version

A judged program must exit 0 and is compared on stdout — so the exercises in
this module print both lines to stdout and the code as a final line:

```
error: division by zero at 1:7
  1 + 2 / 0
        ^
exit 1
```

That `exit 1` line is the exercises' stand-in for `process.exitCode = 1`. The
reference at the bottom of this module is the real thing.
""",
    """
```bash
$ echo '1 + 2 / 0' | node calc.ts; echo "exit: $?"
error: division by zero at 1:7
  1 + 2 / 0
        ^
exit: 1
$ echo '1 + 2' | node calc.ts 2>/dev/null; echo "exit: $?"
3
exit: 0
```

The second run discards stderr and still gets the value.
""",
    pitfalls=[
        "Exit code 0 on a user error. A script cannot tell success from failure without parsing the text.",
        "The same non-zero code for everything. 1 and 2 ask different people to act.",
        "`process.exit(1)` in the middle of `run`. It kills the process before output is flushed in some cases, and makes `run` impossible to test.",
        "Errors on stdout in your real `calc.ts`. `calc.ts < prog > out.txt` then writes the error into the answer file.",
    ],
    warmup=[
        _pq("What exit code should `echo 'y + 1' | node calc.ts` produce?",
            ["1 — the user's program has a mistake",
             "0 — it printed something",
             "2 — it is an error",
             "It depends on the shell"],
            0,
            "Undefined variable is the user's mistake."),
    ],
    exercises=[
        _pex("calc-m17-exit-1", "Your mistake, code 1",
             "In `run`, a failed evaluation becomes the report with exit code 1.",
             _C17_FULL,
             "    return { text: report(src, result.error), code: 1 };",
             _C17_SHALLOW,
             ["Same shape as the scan and parse failures above it.",
              "The report needs the source and the error.",
              "`return { text: report(src, result.error), code: 1 };`"]),
        _pfix("calc-m17-exit-fix1", "Failure that looks like success",
              "`1 + 2 / 0` prints the right report — and `exit 0`. A script "
              "would think it worked.",
              _c17(run=_C17_RUN.replace("    return { text: report(src, result.error), code: 1 };",
                                        "    return { text: report(src, result.error), code: 0 };")),
              _C17_FULL,
              _C17_SHALLOW,
              ["Which outcomes are reported with the wrong code?",
               "Only evaluation errors — scan and parse errors are right.",
               "A user's mistake is code 1."],
              difficulty="Intro"),
        _pch("calc-m17-exit-report", "The report", "Medium",
             "Write `lineOf` and `report`: find the error's line in the source, "
             "and return the formatted message, the line, and a caret under the "
             "column — the line and caret each indented by two spaces.",
             _C17_FULL,
             _C17_REPORT.rstrip("\n"),
             _C17_SHALLOW,
             ["`lineOf`: hop with `src.indexOf(\"\\n\", start) + 1` until the right line, then cut to the next `\\n` or the end.",
              "`-1` from `indexOf` means there is no next line break.",
              "`report`: `formatError(err)`, then the line, then `col - 1` spaces and `^`.",
              "Join the three with `\\n`, each of the last two starting with two spaces."]),
    ],
    quiz=[
        _pq("Why do errors go to stderr in the real `calc.ts`?",
            ["So output redirected to a file or another program contains only values, while errors still reach the person",
             "Because stderr is faster",
             "Because stdout cannot show errors",
             "They should go to stdout"],
            0,
            "Two streams, two audiences."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C17_FINAL = _pch(
    "calc-m17-build", "Module 17 build — errors a stranger can act on", "Hard",
    "Write the end of `calc.ts`, from `lineOf` to the boundary:\n\n"
    "* `lineOf` and `report` — the message, the line, and a caret\n"
    "* `Outcome` and `run` — the value with code 0, or the report with code 1\n"
    "* `main` — one `try` around `run`; anything thrown becomes `error: internal "
    "error: <message>` with code 2\n\n"
    "One test is ten thousand nested brackets.",
    _C17_FULL,
    _cjoin(_C17_REPORT, _C17_RUN, _C17_BOUNDARY).rstrip("\n"),
    _C17_TESTS,
    ["`report` builds three lines joined with `\\n`.",
     "`run` is module 16's, returning an `Outcome` at each exit.",
     "`main`: `try { return run(src, env); } catch (e) { … }`.",
     "`e` is `unknown` — `instanceof Error` before reading `.message`."],
)


_C17_REFERENCE = _stdin(_cjoin(
    _C16_TOKENS, _C16_ERRORS, _C17_NEVER_FN, _C16_SCAN, _C16_TREE, _C13_STMTS, _C17_STATE,
    _c17_defaults(_C16_DESCRIBE), _C16_PRIMARY, _C16_UNARY, _C16_PRODUCT, _C16_SUM,
    _C16_COMPARISON, _C13_PARSE_STMT, _C13_PARSE_PROGRAM, _C16_RESULT, _C14_ENV,
    _c17_defaults(_C16_EVAL), _c17_defaults(_C16_APPLY), _c17_defaults(_C16_EXECUTE),
    _C17_REPORT, _C17_RUN, _C17_BOUNDARY, _C17_REAL_MAIN))


_CALC_MODULES.append(_pmod(
    key="calc-messages", number=17, phase="usable",
    title="Error messages that point at the problem",
    what="a caret under the offending character, and try/catch at the edge",
    goal="Turn every failure into a message a stranger could act on — and a bug into a clean exit.",
    why=_C17_WHY,
    est_minutes=50,
    builds_on=["calc-scan-errors", "calc-never", "calc-positions"],
    concepts=["error reports", "carets", "exceptions vs values", "assertNever",
              "one boundary", "unknown in catch", "exit codes", "stdout vs stderr"],
    deliverable="Every error prints its source line with a `^` under the column; "
                "a bug — or ten thousand nested brackets — becomes `error: internal "
                "error: …` instead of a stack trace; and the exit code is 0, 1 or 2.",
    objectives=[
        "Find a line in the source and draw a caret under a column",
        "Say which failures are values and which are exceptions, with a reason for each",
        "Write `assertNever` and explain its `never` parameter and return type",
        "Put one `try` at the edge of the program and narrow what it catches",
        "Name an exception the program never threw, and show the boundary handling it",
        "Choose exit codes and output streams so a script can use the tool",
    ],
    brief=_C17_BRIEF,
    syntax=_C17_SYNTAX,
    steps=[_C17_S1, _C17_S2, _C17_S3, _C17_S4],
    final_build=_C17_FINAL,
    acceptance=[
        "`echo '1 + )' | node calc.ts` prints `error: unexpected ')' at 1:5`, then `  1 + )`, then a caret under the `)`.",
        "`echo '1 +' | node calc.ts` puts the caret just after the `+`.",
        "An error on line 3 of a program prints line 3.",
        "Ten thousand nested brackets print `error: internal error: Maximum call stack size exceeded` — no stack trace.",
        "`echo '1 + 2' | node calc.ts; echo $?` prints `3` and `0`; a user error exits 1; an internal error exits 2.",
        "Errors are written to stderr, values to stdout.",
        "`throw` appears only in `assertNever` and `peek`; `try` appears exactly once.",
    ],
    manual_test="""
```bash
echo '1 + )'          | node calc.ts; echo "exit $?"     # caret under ), exit 1
echo '1 +'            | node calc.ts; echo "exit $?"     # caret after +, exit 1
printf 'let a = 1;\\nlet b = 0;\\na / b' | node calc.ts     # line 3, caret under /
echo '1 + 2'          | node calc.ts; echo "exit $?"     # 3, exit 0
node -e 'console.log("(".repeat(10000) + "1" + ")".repeat(10000))' | node calc.ts; echo "exit $?"
```

Now check the streams are separate. `echo '1 / 0' | node calc.ts 2>/dev/null`
prints nothing — the error went to stderr — and `echo '1 + 2' | node calc.ts
2>/dev/null` still prints `3`.

Last, prove `assertNever` still does module 10's job: add `| { kind: "abs"; operand:
Expr; pos: Pos }` to `Expr` and compile. `Argument of type '…' is not assignable
to parameter of type 'never'` — the forgotten case, named, exactly as before.
""",
    reference="""// calc.ts — module 17
//
// Two kinds of failure, handled two ways:
//   * the USER's mistakes are values, all the way out, reported with the line
//     and a caret under the column — exit code 1;
//   * the PROGRAM's impossibilities throw (assertNever, peek past the end), and
//     one try/catch at the edge turns anything thrown — including JavaScript's
//     own stack overflow — into `error: internal error: …`, exit code 2.
// Values go to stdout, errors to stderr, and process.exitCode tells the shell.
""" + _C17_REFERENCE,
    stretch=[
        "Replace the stack overflow with a proper limit: count bracket depth in `parsePrimary` and fail with `expression nested too deeply` at the offending `(`. Then it is the user's error again, with a caret — which is where it belongs.",
        "Underline a whole span instead of one character: `^^^^^` under `2 / 0`. You need module 16's stretch (a start and end position per node).",
        "Colour the output when stderr is a terminal: red `error:`, bold caret. Find out how a program knows whether it is writing to a terminal, and why it should not colour otherwise.",
        "Add a `--json` flag that prints errors as `{\"message\":…,\"line\":…,\"col\":…}` for editors to consume. It needs nothing from the error but what `CalcError` already holds — which is the argument for errors as data.",
    ],
    glossary=[
        _pgloss("caret", "The `^` printed under the column an error refers to."),
        _pgloss("exception", "A thrown value that unwinds every caller until caught. Here, only for failures a bug can cause."),
        _pgloss("assertNever", "A function taking `never` and returning `never`: a compile-time exhaustiveness check that throws if it ever runs."),
        _pgloss("boundary", "The one place at the edge of a program that catches exceptions and turns them into a clean result."),
        _pgloss("exit code", "The number a process reports to the shell. 0 is success; this tool uses 1 for user errors and 2 for internal ones."),
        _pgloss("stderr", "The output stream for errors and diagnostics, separate from stdout's results."),
    ],
    cheatsheet="""
```ts
function report(src: string, err: CalcError): string {
  const caret = " ".repeat(err.pos.col - 1) + "^";
  return `${formatError(err)}\\n  ${lineOf(src, err.pos.line)}\\n  ${caret}`;
}

function assertNever(x: never): never {                  // bugs throw
  throw new Error(`unhandled case: ${JSON.stringify(x)}`);
}

function main(src: string, env: Env): Outcome {          // ONE try, at the edge
  try {
    return run(src, env);                                // values inside
  } catch (e) {
    let detail = "unknown";
    if (e instanceof Error) { detail = e.message; }
    return { text: `error: internal error: ${detail}`, code: 2 };
  }
}

if (outcome.code === 0) { console.log(outcome.text); } else { console.error(outcome.text); }
process.exitCode = outcome.code;
```

```
error: unexpected ')' at 1:5
  1 + )
      ^
```

| Code | Meaning |
|---|---|
| 0 | a value |
| 1 | the user's program has a mistake |
| 2 | calc has a bug (or ran out of stack) |

| Symptom | Cause |
|---|---|
| caret one to the right | `.repeat(col)` instead of `.repeat(col - 1)` |
| stack trace on deep nesting | no `try` at the edge |
| failure exits 0 | `Outcome.code` left at 0 for an error |
""",
    self_check=[
        "Can you draw the report for an error at 2:5 in a two-line program?",
        "Can you state the rule for when to return a failure and when to throw?",
        "Can you explain what the `never` parameter and the `never` return type of `assertNever` each do?",
        "Can you name an exception `calc.ts` never throws itself, and what happens to it?",
        "Can you give the three exit codes and who should act on each?",
    ],
    review=[
        _pq("Which failures does `calc.ts` throw?",
            ["Only ones a bug can cause — `assertNever` and `peek` past the end",
             "All of them",
             "Evaluation errors",
             "None"],
            0,
            "User mistakes stay values."),
        _pq("Why is there exactly one `try` in the program?",
            ["Expected failures are values handled by their callers; exceptions only need catching once, at the edge, to end cleanly",
             "TypeScript allows only one",
             "For speed",
             "There are four"],
            0,
            "Results as values inside, one catch outside."),
        _pq("What does `assertNever(e)` do at compile time?",
            ["Fails to compile unless `e` has been narrowed to `never` — module 10's check",
             "Nothing",
             "Throws",
             "Adds a missing case"],
            0,
            "Its runtime job is the `throw`."),
        _pq("Ten thousand nested brackets — why an internal error rather than a parse error?",
            ["The parser recurses once per bracket and JavaScript runs out of call stack, throwing a `RangeError` the boundary catches",
             "Because brackets must match",
             "Because the scanner rejects them",
             "It is a parse error"],
            0,
            "An exception nobody wrote `throw` for."),
        _pq("Why print the caret `col - 1` spaces in?",
            ["The caret occupies the column itself; column 1 needs no spaces before it",
             "Because columns count from 0",
             "To leave room for the indent",
             "It should be `col` spaces"],
            0,
            "Off by one here puts every caret beside the mistake."),
    ],
    milestone="`calc.ts` tells a stranger exactly what they got wrong and where, "
              "with the line and a caret; it never shows a stack trace; and a script "
              "can tell success, a user's mistake and a bug apart by the exit code. "
              "One module left: a REPL, and tests you wrote yourself.",
))
