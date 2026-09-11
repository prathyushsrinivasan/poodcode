# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc — a small expression language. The Projects track's second project.
#
# exec()'d by tools/projects_track.py inside its namespace; defines `_CALC` and
# may use any helper from the parent (`_pmod`, `_pskel`, `_pstep`, `_pex`,
# `_pch`, `_pfix`, `_syn`, `_phase`, `_plain`, `_stdin`, the lints).
#
# WHY THIS PROJECT, next to the Todo API:
#
#   The Todo API teaches the shape of a service. Its data arrives as text from
#   somewhere else, and its hard parts are contracts — status codes, validation,
#   error envelopes. Almost none of it stresses the type system, because HTTP
#   hands you strings and takes strings back.
#
#   A language processor is the mirror image. It is three transformations over
#   data you designed yourself — text → tokens → tree → value — and every one of
#   them is a discriminated union walked recursively. That makes it the natural
#   home for the half of TypeScript the Todo API never reaches: unions with a
#   `kind` tag, types that refer to themselves, narrowing that has to be
#   exhaustive, and a compiler that lists every place you forgot when the union
#   grows a member.
#
#   The two projects share no subject matter at all, which is the point. Someone
#   who has finished both has written the two programs most jobs are made of.
#
# THE PROGRAM SHAPE: `_stdin`. Module 1 is `_plain` (there is nothing to read
# yet — it designs the token type), and from module 2 the source text arrives on
# stdin and the answer goes to stdout. No server, so no replayer: every program
# here is entirely the learner's, and `_authored_region` is a no-op on it.
#
# DETERMINISM is free in this project — no ports, no ids, no clock. The only
# rule worth stating is that error text is part of the contract: an exercise
# that prints `error: unexpected '$' at 1:3` is judged on that text, so the
# format is decided in module 4 and never drifts afterwards.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Scope: the module that first introduces each token, for THIS project.
#
# Same two lints as the Todo API, different syllabus — see the note above
# `_TODO_SCOPE_RULES`. Some tokens land in a very different place here: `.split(`
# is a module 10 tool for pulling an id out of `/todos/7`, and a module 18 tool
# for cutting stdin into REPL lines, because that is genuinely the first time
# this project needs it.
#
# Deliberately ungated (module 1 uses all of them, so a rule would be a false
# claim): `const`, `let`, `function`, `return`, `if`, `else`, template literals
# and `===`. Module 1's syntax primer covers what it needs of them.
# ---------------------------------------------------------------------------

_CALC_SCOPE_RULES = [
    # --- Phase 1: scan (text → tokens) -------------------------------------
    ("type ", 1),
    ("interface ", 99),        # the track uses `type` throughout; see Todo m1
    ("JSON.stringify(", 1),
    (".kind", 1),              # the discriminant every union in this project turns on
    # Arrays, the loop that fills one, and the stdin the loop reads all arrive
    # together in module 2. A scanner IS a loop that pushes onto a list, and no
    # half of that is useful on its own.
    ("[]", 2),
    (".push(", 2),
    ("while (", 2),
    ("for (", 2),
    (".length", 2),
    (".charAt(", 2),
    # A digit's position in "0123456789" is its value, so module 2 reads single
    # digits with `.indexOf(` before `Number` and `.slice(` exist (module 3).
    (".indexOf(", 2),
    ("readFileSync(", 2),
    (".trim(", 2),
    (".slice(", 3),
    ("Number(", 3),
    # Module 4's whole argument is that a scan failure is a VALUE. `ok: true` is
    # the literal type that makes the result union discriminated, and it is the
    # first boolean literal used as a type in this project.
    ("ok: true", 4),
    # Columns must be positions in what the user TYPED, and `.trim()` removes
    # leading spaces too — so module 4 switches the source read to `.trimEnd()`.
    (".trimEnd(", 4),
    # --- Phase 2: parse (tokens → a tree) ----------------------------------
    # `Expr` is the recursive type module 5 exists to introduce; no earlier
    # program may so much as mention it.
    (": Expr", 5),
    # --- Phase 3: evaluate (tree → a value) --------------------------------
    ("switch (", 9),
    ("case ", 9),
    ("never", 10),
    ("Number.isFinite(", 11),
    # --- Phase 4: a language, not a calculator -----------------------------
    ("new Map", 12),
    (".set(", 12),
    (".get(", 12),
    ("typeof ", 14),
    # --- Phase 5: make it usable -------------------------------------------
    # `throw` waits until module 17 for a reason: everything before it returns
    # its failures, and an uncaught throw in a judged program is a crash rather
    # than an answer. 17 is where the boundary that catches one gets written.
    ("try {", 17),
    ("catch ", 17),
    ("throw ", 17),
    (".repeat(", 17),
    (".split(", 18),
    ("=>", 18),
    (".map(", 18),
    # --- Never. Type-stripping cannot run these (design rule 4). -----------
    ("enum ", 999),
    ("namespace ", 999),
    ("declare ", 999),
]

_CALC_PHASES = [
    _phase("scan", "Phase 1 · Scan the text",
           "`1 + 2 * 3` becomes a list of tokens you can print — and `1 $ 2` becomes an error that says which character and where.",
           "Text is a bad thing to compute with. Turn it into a list of small, "
           "typed facts first, and every module after this one gets shorter."),
    _phase("parse", "Phase 2 · Build the tree",
           "A tree that already knows `1 + 2 * 3` is an addition whose right-hand side is a multiplication.",
           "A list of tokens is flat and arithmetic is not. This is where "
           "precedence stops being a rule you remember and becomes a shape."),
    _phase("eval", "Phase 3 · Evaluate the tree",
           "Text in, a number out. `calc.ts` is a working calculator you can pipe things into.",
           "Walking the tree is the easiest phase in the project — which is the "
           "whole return on having built the right tree in phase 2."),
    _phase("lang", "Phase 4 · A language, not a calculator",
           "`let x = 4; x * x > 10` — variables, statements and booleans, all evaluated in order.",
           "Three features, each of which forces a change one layer down. This is "
           "where you find out whether the first three phases were built well."),
    _phase("usable", "Phase 5 · Make it usable",
           "`error: unexpected ')' at 1:7`, a caret pointing at the character, and a REPL to type into.",
           "The difference between a program you wrote and a tool someone else "
           "can use is entirely in what it says when they get it wrong."),
]

# Authored modules live one per file in tools/calc_mNN_*.py, each appending to
# `_CALC_MODULES`; the rest are skeletons below. Order matters —
# `_lint_structure` checks it positionally.
_CALC_MODULE_FILES = (
    "calc_m01_token.py",
    "calc_m02_scan.py",
    "calc_m03_numbers.py",
    "calc_m04_errors.py",
)

_CALC_MODULES = []

for _cfname in _CALC_MODULE_FILES:
    _cpath = os.path.join(HERE, _cfname)
    assert os.path.exists(_cpath), f"missing calc module file: {_cfname}"
    with open(_cpath, encoding="utf-8") as _cf:
        exec(compile(_cf.read(), _cpath, "exec"))

# --- Planned modules -------------------------------------------------------
# Delete a line here as its file lands in `_CALC_MODULE_FILES` above.
_CALC_MODULES += [
    _pskel("calc-tree", 5, "parse", "What a tree is",
           "a type that refers to itself, and the shape `1 + 2 * 3` really has",
           "Define `Expr` and build one by hand.",
           "The tree the parser is going to produce, written down as a type."),
    _pskel("calc-cursor", 6, "parse", "A parser with a cursor",
           "peek, advance and expect — reading a list of tokens in order",
           "Parse a single number token into an `Expr`.",
           "The parser can consume tokens and say when it did not get what it wanted."),
    _pskel("calc-precedence", 7, "parse", "Precedence, and why `1 + 2 * 3` is 7",
           "two functions calling each other is the entire trick",
           "Parse `+ - * /` into a tree that binds them in the right order.",
           "The tree is correct for any mix of the four operators."),
    _pskel("calc-parens", 8, "parse", "Parentheses and unary minus",
           "recursion back to the top of the grammar, which closes the loop",
           "Parse `(1 + 2) * -3`.",
           "The grammar is complete: any arithmetic expression parses."),
    _pskel("calc-walk", 9, "eval", "Walking the tree",
           "switch on the kind, recurse into the children, return a number",
           "Turn an `Expr` into the number it means.",
           "`echo '1 + 2 * 3' | node calc.ts` prints 7."),
    _pskel("calc-never", 10, "eval", "Exhaustiveness with `never`",
           "the compiler proving you handled every node, forever",
           "Make a new node kind a compile error everywhere it is not handled.",
           "Growing the language can no longer silently break the evaluator."),
    _pskel("calc-arithmetic", 11, "eval", "Division, and the arithmetic that can fail",
           "what your language says about `1 / 0`, decided rather than inherited",
           "Give division a defined answer for every input.",
           "No expression evaluates to `Infinity` or `NaN` by accident."),
    _pskel("calc-vars", 12, "lang", "Variables and an environment",
           "`let x = 4` — a Map, and the name that is not in it",
           "Bind a name to a value and read it back.",
           "The language has memory."),
    _pskel("calc-statements", 13, "lang", "Statements, and a program",
           "many expressions separated by `;`, and what a program's value is",
           "Run `let x = 4; x * x` as one program.",
           "A program is a sequence, not a single expression."),
    _pskel("calc-booleans", 14, "lang", "Booleans and comparison",
           "the value type stops being `number`, and every layer notices",
           "Evaluate `2 < 3` without letting `true * 2` sneak through.",
           "Values are `number | boolean`, and the type errors that implies are handled."),
    _pskel("calc-if", 15, "lang", "`if` as an expression",
           "a conditional that has a value, and the type rule that forces",
           "Evaluate `if 2 < 3 then 10 else 20`.",
           "The language can make a decision."),
    _pskel("calc-positions", 16, "usable", "Line and column on every token",
           "carry the position from the scanner, or you can never report it",
           "Attach a position to every token and every node.",
           "Every token knows where it came from."),
    _pskel("calc-messages", 17, "usable", "Error messages that point at the problem",
           "a caret under the offending character, and try/catch at the edge",
           "Turn every failure into a message a stranger could act on.",
           "One error format, one place that prints it, no stack traces."),
    _pskel("calc-repl", 18, "usable", "A REPL, and a test suite you wrote",
           "read stdin line by line, and prove the whole thing with no framework",
           "Leave the language in a shape you would be happy to add a feature to.",
           "The finished language — interactive, tested, and yours."),
]

_lint_scope(_CALC_MODULES, _CALC_SCOPE_RULES)
_lint_syntax_taught(_CALC_MODULES, _CALC_SCOPE_RULES)

_CALC = {
    "key": "calc-lang",
    "number": 2,
    "title": "Calc",
    "tagline": "Text in, a number out — a tokenizer, a parser and an evaluator, written from nothing.",
    "language": "typescript",
    "goal": "Build a small expression language in TypeScript — scanner, parser, "
            "evaluator and error reporting — that runs `let x = 4; x * x` and "
            "tells you exactly where you went wrong when it cannot.",
    "why": "Everything that reads text and does something structured with it is "
           "this program with more cases in it: compilers, linters, formatters, "
           "query parsers, template engines, config loaders. It is also the "
           "shortest route to the half of TypeScript the Todo API never needs — "
           "unions you walk recursively, and a compiler that tells you which "
           "branch you forgot.",
    "authored": True,
    "est_minutes": 18 * 40,
    "stack": ["TypeScript", "node:fs", "zero dependencies", "no framework"],
    "completion_note": "A module completes once you have read it through and "
                       "solved its exercises — but the real deliverable is "
                       "`calc.ts` on your own machine, evaluating something you "
                       "typed yourself.",
    "brief": _pbp("""
### What you are building

A **language**. A small one — arithmetic, variables, comparison and `if` — but a
real one, with the three pieces every language has. When you are done, this
works against a file on your own machine:

```
$ echo '1 + 2 * 3' | node calc.ts
7

$ echo '(1 + 2) * -3' | node calc.ts
-9

$ echo 'let x = 4; x * x > 10' | node calc.ts
true

$ echo '1 + )' | node calc.ts
error: unexpected ')' at 1:5
  1 + )
      ^
```

That last block is the one worth looking at twice. Any evening gets you a
calculator; the difference between a calculator and a language is that the
language can tell a stranger what they typed wrong and where.

### The three pieces

Every language processor ever written is the same pipeline, and this project is
one phase per arrow:

```
  "1 + 2 * 3"   →   [num 1, op +, num 2, op *, num 3, eof]   →   (+ 1 (* 2 3))   →   7
      text            tokens                                       tree             value
                    ── scanner ──                            ── parser ──      ── evaluator ──
```

Each arrow throws away something you no longer need and adds something you do.
The scanner throws away whitespace and gains types. The parser throws away
order-of-appearance and gains **structure** — which is where `1 + 2 * 3` stops
being five tokens in a row and becomes an addition whose right-hand side is a
multiplication. The evaluator throws away the structure and gains an answer.

Nothing here is a simplification of how real ones work. It is how real ones
work, with four operators instead of forty.

### What it will teach you that the Todo API cannot

The Todo API is about contracts between programs. This one is about **data you
designed yourself**, and it leans on the part of TypeScript that exists for
exactly that:

| Idea | Where it lands | Why it matters outside this project |
|---|---|---|
| Discriminated unions | Module 1, and then everywhere | The single most useful modelling tool the language has |
| Recursive types | Module 5 | Trees, JSON, file systems, comment threads |
| Exhaustive narrowing with `never` | Module 10 | Adding a case becomes a compile error, not a bug report |
| Errors as values | Module 4, paid off in 17 | The alternative to exceptions, and usually the better one |

### How it is broken up

**18 modules in 5 phases.** A module is one sitting — 30 to 50 minutes — and
adds exactly one capability. Every module tells you *why it exists* before it
tells you what to type, teaches every piece of syntax it needs before using it,
walks you through the build in ordered steps with a checkpoint each, gives you
judged exercises to write yourself, and ends with a reference you can reveal and
compare against.

You are never asked to write a line of TypeScript this project has not already
put in front of you. That is enforced at build time, not promised in prose.
"""),
    "endpoints": [],
    "setup": _pbp("""
You need **Node 22 or newer** — it runs `.ts` files directly by stripping the
type annotations, so there is no build step and nothing to install.

```bash
mkdir calc && cd calc
```

Everything lives in one file until module 18. Create `calc.ts` and feed it a
program on stdin:

```bash
echo '1 + 2' | node calc.ts
```

On Windows PowerShell, `echo` behaves differently — use a file instead:

```powershell
'1 + 2' | node calc.ts
```

> **A word on the type-check.** Running a `.ts` file *strips* the types; it does
> not check them. Node will happily run `const n: number = "seven"`. The
> exercises here are type-checked before they run, so they catch it — but on
> your own machine, install TypeScript (`npm i -D typescript`) and run
> `npx tsc --noEmit --strict calc.ts` when something surprises you.

Two flags are worth turning on from the start, because this project is built
around both: `strict`, and `noUncheckedIndexedAccess`. The second one is why
`tokens[i]` has type `Token | undefined` here — and a parser that walks off the
end of its token list is the most common bug in this kind of program, so being
made to think about it is the feature.
"""),
    "roadmap": _CALC_PHASES,
    "modules": _CALC_MODULES,
    "acceptance": [
        "`echo '1 + 2 * 3' | node calc.ts` prints `7` — not `9`.",
        "`echo '(1 + 2) * -3' | node calc.ts` prints `-9`.",
        "`echo 'let x = 4; x * x' | node calc.ts` prints `16`.",
        "`echo '2 < 3' | node calc.ts` prints `true`, and `echo 'true * 2'` is a reported error rather than `NaN`.",
        "`echo '1 $ 2' | node calc.ts` names the character and its column, and exits without printing a stack trace.",
        "`echo '1 +' | node calc.ts` says the input ended early. It never prints `NaN`.",
        "`echo 'y + 1' | node calc.ts` says `y` is not defined, rather than quietly treating it as zero.",
        "Adding a new member to the `Expr` union makes the compiler list every place that now has to handle it.",
    ],
    "manual_test": _pbp("""
With `calc.ts` finished, drive it from a shell:

```bash
# arithmetic and precedence
echo '1 + 2 * 3'        | node calc.ts     # 7
echo '(1 + 2) * 3'      | node calc.ts     # 9
echo '10 / 4'           | node calc.ts     # 2.5
echo '-4 + 10'          | node calc.ts     # 6

# it is a language, not a calculator
echo 'let x = 4; x * x'          | node calc.ts     # 16
echo 'let x = 4; x * x > 10'     | node calc.ts     # true
echo 'if 2 < 3 then 10 else 20'  | node calc.ts     # 10

# the failure paths — these matter more
echo '1 $ 2'    | node calc.ts     # unexpected character
echo '1 +'      | node calc.ts     # ended early
echo '1 + )'    | node calc.ts     # unexpected token, with a caret
echo 'y + 1'    | node calc.ts     # undefined variable
echo '1 / 0'    | node calc.ts     # whatever you decided in module 11
```

Then check the exit codes with `echo $?`. A tool that prints an error and exits
0 is a tool nobody can put in a script — which is the whole subject of module 17.
"""),
    "stretch": [
        "Add `%` and `**`, and work out from your own parser where each belongs on the precedence ladder. `**` is right-associative; find out what that costs you.",
        "Add strings, and a `+` that concatenates them. Then follow the change: the token union, the value union, every comparison, and every error message.",
        "Add `fn double(n) = n * 2` and calls. You will need a call expression, a scope that nests, and a decision about what happens when the argument count is wrong.",
        "Print the tree as an indented drawing instead of JSON, so precedence is something you can see rather than something you trust.",
        "Add a `--tokens` flag that stops after phase 1 and prints the token list. Every real compiler has one, because it is how you find out which phase is lying to you.",
        "Write a formatter: parse the input and print it back out with canonical spacing and only the parentheses that are needed. It reuses the whole front end and nothing of the evaluator.",
    ],
    "milestone": "You have written a language — a scanner, a parser, an "
                 "evaluator, and the error reporting that makes it usable by "
                 "someone who is not you. Every compiler, linter, formatter, "
                 "template engine and query parser you will ever open is this "
                 "program with more cases in it.",
}

_lint_structure(_CALC)
