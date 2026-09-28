# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 13 — Statements, and a program.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses module 12's program.
#
# THE CONTRACT CHANGE. The parser's entry point stops returning an `Expr`: it
# returns a PROGRAM — `Stmt[]` — and "expression" and "program" stop being the
# same word. A statement is `let NAME = EXPR` or a bare expression; statements
# are separated by `;`, and a trailing `;` is allowed.
#
# THE KEYWORD. `let` is scanned by the identifier branch and then recognised —
# a word, not a character class — which makes it RESERVED: `let let = 1` is
# `error: expected a name but found 'let'`. Keywords later (true/false, if/then/
# else) extend the same `if (word === …)` check.
#
# A PROGRAM'S VALUE is the value of its last statement, and a `let` statement's
# value is the value it bound — so `let x = 4` alone prints 4. Decided and
# stated in step 4. The environment now starts EMPTY (module 12's seeded names
# are gone): a program writes into it with `let`, statements run in order, and
# `x; let x = 1` fails because the first statement runs first.
#
# An empty `Stmt[]` has no value. The parser never produces one — every program
# has at least one statement — but the TYPE allows it, so `runProgram` starts
# from `error: empty program` and says why in a comment-free way in step 4's text.
#
# Three result unions become five (StmtResult, ProgramResult). A generic
# `Result<T>` is the obvious refactor and stays in the stretch list; the module
# notes the pressure rather than hiding it.
# ---------------------------------------------------------------------------

_C13_TOKENS = """type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type IdentToken = { kind: "ident"; name: string };
type LetToken = { kind: "let" };
type EqualsToken = { kind: "equals" };
type SemiToken = { kind: "semi" };
type LParenToken = { kind: "lparen" };
type RParenToken = { kind: "rparen" };
type EofToken = { kind: "eof" };

type Token =
  | NumberToken
  | OpToken
  | IdentToken
  | LetToken
  | EqualsToken
  | SemiToken
  | LParenToken
  | RParenToken
  | EofToken;

function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

function opToken(op: Op): OpToken {
  return { kind: "op", op: op };
}

function identToken(name: string): IdentToken {
  return { kind: "ident", name: name };
}

function letToken(): LetToken {
  return { kind: "let" };
}

function equalsToken(): EqualsToken {
  return { kind: "equals" };
}

function semiToken(): SemiToken {
  return { kind: "semi" };
}

function lparenToken(): LParenToken {
  return { kind: "lparen" };
}

function rparenToken(): RParenToken {
  return { kind: "rparen" };
}

function eofToken(): EofToken {
  return { kind: "eof" };
}
"""

_C13_WORD = """      const word = src.slice(start, i);
      if (word === "let") {
        tokens.push(letToken());
      } else {
        tokens.push(identToken(word));
      }
"""

_C13_PUNCT = """    } else if (ch === "=") {
      tokens.push(equalsToken());
      i = i + 1;
    } else if (ch === ";") {
      tokens.push(semiToken());
      i = i + 1;
"""

_C13_SCAN = _C12_SCAN.replace("      tokens.push(identToken(src.slice(start, i)));\n", _C13_WORD, 1) \
    .replace("\n    } else {\n      return { ok: false", "\n" + _C13_PUNCT + "    } else {\n      return { ok: false", 1)

_C13_DESCRIBE = _C12_DESCRIBE.replace(
    '    case "lparen":',
    '    case "let":\n      return "\'let\'";\n    case "equals":\n      return "\'=\'";\n'
    '    case "semi":\n      return "\';\'";\n    case "lparen":', 1)

_C13_STMTS = """type LetStmt = { kind: "let"; name: string; value: Expr };
type ExprStmt = { kind: "expr"; expr: Expr };

type Stmt = LetStmt | ExprStmt;
"""

_C13_PARSE_STMT = """type StmtResult = { ok: true; stmt: Stmt } | Failure;

function parseStatement(p: Parser): StmtResult {
  if (peek(p).kind !== "let") {
    const e = parseExpr(p);
    if (!e.ok) {
      return e;
    }
    return { ok: true, stmt: { kind: "expr", expr: e.expr } };
  }
  advance(p);
  const name = advance(p);
  if (name.kind !== "ident") {
    return expected("a name", name);
  }
  const eq = advance(p);
  if (eq.kind !== "equals") {
    return expected("'='", eq);
  }
  const value = parseExpr(p);
  if (!value.ok) {
    return value;
  }
  return { ok: true, stmt: { kind: "let", name: name.name, value: value.expr } };
}
"""

_C13_PARSE_PROGRAM = """type ProgramResult = { ok: true; program: Stmt[] } | Failure;

function parseProgram(tokens: Token[]): ProgramResult {
  const p: Parser = { tokens: tokens, pos: 0 };
  const program: Stmt[] = [];
  while (true) {
    const s = parseStatement(p);
    if (!s.ok) {
      return s;
    }
    program.push(s.stmt);
    const t = advance(p);
    if (t.kind === "eof") {
      return { ok: true, program: program };
    }
    if (t.kind !== "semi") {
      return unexpectedToken(t);
    }
    if (peek(p).kind === "eof") {
      return { ok: true, program: program };
    }
  }
}
"""

_C13_EXECUTE = """function execute(s: Stmt, env: Env): EvalResult {
  switch (s.kind) {
    case "let": {
      const result = evaluate(s.value, env);
      if (!result.ok) {
        return result;
      }
      env.set(s.name, result.value);
      return result;
    }
    case "expr":
      return evaluate(s.expr, env);
    default: {
      const impossible: never = s;
      return impossible;
    }
  }
}

function runProgram(program: Stmt[], env: Env): EvalResult {
  let last: EvalResult = { ok: false, error: "error: empty program" };
  for (const s of program) {
    last = execute(s, env);
    if (!last.ok) {
      return last;
    }
  }
  return last;
}
"""

_C13_RUN_FN = """function run(src: string, env: Env): string {
  const scanned = scan(src);
  if (!scanned.ok) {
    return scanned.error;
  }
  const parsed = parseProgram(scanned.tokens);
  if (!parsed.ok) {
    return parsed.error;
  }
  const result = runProgram(parsed.program, env);
  if (!result.ok) {
    return result.error;
  }
  return `${result.value}`;
}
"""

_C13_MAIN = """const env: Env = new Map();
console.log(run(readFileSync(0, "utf8").trimEnd(), env));
"""


def _c13(tokens=_C13_TOKENS, scan=_C13_SCAN, describe=_C13_DESCRIBE,
         stmt=_C13_PARSE_STMT, program=_C13_PARSE_PROGRAM, execute=_C13_EXECUTE,
         run=_C13_RUN_FN, main=_C13_MAIN):
    return _stdin(_cjoin(tokens, _C6_RESULTS, _C4_UNEXPECTED, scan, _C12_TREE, _C13_STMTS,
                         _C6_STATE, describe, _C12_PRIMARY, _C8_UNARY, _C8_PRODUCT, _C7_SUM,
                         stmt, program, _C11_RESULT, _C12_ENV, _C12_EVAL, _C11_ARITH,
                         execute, run, main))


_C13_FULL = _c13()

_C13_INPUTS = ["let x = 4; x * x", "let x = 4", "let x = 2; let y = x * 3; y + x",
               "1; 2; 3", "let x = 1;", "let x = 1; let x = x + 1; x",
               "x; let x = 1", "let a = 1; b", "let = 4", "let x 4", "let x = 4 x",
               ";", "1 + 2;;", "let let = 1", "let x = 10; x / (x - 10)", "",
               "1 + 2 * 3", "let x = 4; x $ 2"]
_C13_TESTS = _ctests(13, _C13_INPUTS)

_C13_WHY = (
    "The language has names and nowhere to write them from. Module 12's "
    "environment was filled in by the program around the language — the user "
    "could read `week`, but could never say what `week` was. That needs a "
    "different kind of thing in the source: not an expression, which has a "
    "value, but a statement, which *does* something. `let x = 4` binds a name; "
    "`x * x` uses it; and a `;` between them makes a program. It is a small "
    "module with one big consequence — the parser stops returning an expression "
    "and starts returning a list of statements — and it is the point at which "
    "\"expression\" and \"program\" stop meaning the same thing."
)

_C13_BRIEF = """
### The whole module in one line

`let x = 4; x * x` prints `16` — a program is a list of statements run in order
against one environment, and its value is the value of the last one.

### Expressions and statements

| | Has a value | Changes something | Example |
|---|---|---|---|
| **expression** | yes | no | `x * x` |
| **statement** | … | yes | `let x = 4` |

Until now the whole input was one expression. Now it is a sequence of
**statements** separated by `;`, and there are two kinds:

```ts
type LetStmt = { kind: "let"; name: string; value: Expr };
type ExprStmt = { kind: "expr"; expr: Expr };
type Stmt = LetStmt | ExprStmt;
```

A `let` statement evaluates its expression and binds the name to the result. An
expression statement just evaluates its expression.

### The contract changes

```ts
function parseProgram(tokens: Token[]): ProgramResult     // was: parse(…) → ParseResult
```

The parser's entry point returns `Stmt[]`, not `Expr`. Everything that called
`parse` changes — which in `calc.ts` is exactly one function, `run`. That is the
payoff of every stage having a single entry point.

### A program's value

A calculator prints an answer, so a program needs one. Decided here:

- **A program's value is the value of its last statement.** `1; 2; 3` is `3`.
- **A `let`'s value is the value it bound.** `let x = 4` on its own prints `4`.
- **Statements run in order**, against one environment that starts empty.
  `x; let x = 1` fails, because the first statement runs first.

### `let` is a keyword

`let` looks like a name and is scanned like one — then recognised. That makes it
**reserved**: `let let = 1` is `error: expected a name but found 'let'`. Every
keyword to come — `true`, `if`, `then` — works the same way.
"""

_C13_SYNTAX = [
    _syn(
        "type Stmt = LetStmt | ExprStmt;",
        "A second tree union, one level above `Expr`: a program is a list of "
        "these. Each member holds `Expr`s; neither is one.",
        """
type LetStmt = { kind: "let"; name: string; value: Expr };
type ExprStmt = { kind: "expr"; expr: Expr };
""",
        "The tags can repeat tags from other unions — `LetStmt`'s `\"let\"` and "
        "`LetToken`'s `\"let\"` never meet, because a `Stmt` and a `Token` are "
        "never in the same union.",
    ),
    _syn(
        "if (word === \"let\") { tokens.push(letToken()); } else { … }",
        "A keyword: scanned as a name, then recognised by comparing the text.",
        "",
        "Recognising keywords *after* scanning the name means `letter` is a name "
        "and `let` is a keyword — the check is on the whole word, never a prefix.",
    ),
    _syn(
        "while (true) { … }",
        "A loop with no condition of its own — it runs until something inside "
        "it returns.",
        """
while (true) {
  const s = parseStatement(p);
  if (!s.ok) {
    return s;
  }
  …
  if (t.kind === "eof") {
    return { ok: true, program: program };
  }
}
""",
        "Every way out is a `return`. The compiler knows a `while (true)` loop "
        "cannot end on its own, so it does not ask for a `return` after it.",
    ),
    _syn(
        "let last: EvalResult = { ok: false, error: \"error: empty program\" };",
        "A variable that holds the most recent statement's result, annotated "
        "with the union so it can hold a success later.",
        "",
        "Without the annotation, `last` would be inferred as the failure member "
        "only, and assigning a success to it would not compile.",
    ),
    _syn(
        "program.push(s.stmt);",
        "Module 2's `.push`, building the list of statements the way the scanner "
        "built the list of tokens.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — three tokens, one of them a word.
# ---------------------------------------------------------------------------

_C13_S1 = _pstep(
    "keyword", "Three tokens, one of them a word",
    "`=`, `;`, and `let` — a name the scanner recognises after reading it.",
    """
Two of the new tokens are single characters, and get module 8's treatment:

```ts
} else if (ch === "=") {
  tokens.push(equalsToken());
  i = i + 1;
} else if (ch === ";") {
  tokens.push(semiToken());
  i = i + 1;
}
```

The third is a **word**. `let` is made of letters, so the identifier branch reads
it — and only once the whole word has been read can the scanner tell it apart
from a name:

```ts
const word = src.slice(start, i);
if (word === "let") {
  tokens.push(letToken());
} else {
  tokens.push(identToken(word));
}
```

That order — read the whole word, then decide — matters. `letter` starts with
`let`, and is a perfectly good name. Checking whole words means it stays one.

### Reserved

Because the scanner turns `let` into its own kind of token before the parser
ever sees it, `let` can never be a name. `let let = 1` fails: the parser wanted a
name after `let` and got a `let` token. That is what **reserved word** means, and
every keyword this language adds will be reserved the same way.

### The compiler's list, again

Three new members of `Token`, and `describe`'s `never` check names all three.
Each gets a case: `'let'`, `'='`, `';'`.
""",
    """
```bash
$ echo 'let x = 4' | node calc.ts
4
$ echo 'let let = 1' | node calc.ts
error: expected a name but found 'let'
```

(Once steps 2 to 4 are done — the scanner is only the first stage.)
""",
    pitfalls=[
        "Checking for keywords before reading the whole word — `src.slice(i, i + 3) === \"let\"` — turns `letter` into `let` followed by `ter`.",
        "Not recognising `let` at all. `let x = 4` scans as three names and an `=`, and the parser reports `unexpected 'x'`.",
        "Scanning `=` as an operator. It does not combine two values; it belongs to the `let` statement's shape, and module 14 needs `==` to be the operator.",
    ],
    warmup=[
        _pq("How does `letter = 1` scan?",
            ["name `letter`, `=`, number 1 — keywords are recognised on whole words",
             "`let`, name `ter`, `=`, 1",
             "An error",
             "`let`, `=`, 1"],
            0,
            "Read the word, then decide."),
    ],
    exercises=[
        _pex("calc-m13-keyword-1", "A word that is a keyword",
             "After reading a word, decide whether it is the keyword `let` or a "
             "name, and push the right token.",
             _C13_FULL,
             _C13_WORD.rstrip("\n"),
             _C13_TESTS,
             ["First cut the word out with `slice`.",
              "Compare the whole word with `\"let\"`.",
              "`letToken()` for the keyword, `identToken(word)` for anything else."]),
        _pfix("calc-m13-keyword-fix1", "`let` is just a name",
              "`let x = 4` says `error: unexpected 'x'`. The parser saw a "
              "variable called `let`, then a stray `x`.",
              _c13(scan=_C13_SCAN.replace(_C13_WORD, "      tokens.push(identToken(src.slice(start, i)));\n")),
              _C13_FULL,
              _C13_TESTS,
              ["What token does the scanner produce for the word `let`?",
               "The parser checks for a `let` token, and never gets one.",
               "Cut the word out, compare it with `\"let\"`, and push `letToken()` when it matches."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why is `let` reserved — unusable as a variable name?",
            ["The scanner turns the word into a `let` token before the parser sees it, so it can never arrive as a name",
             "Because the Map refuses it",
             "Because TypeScript reserves it",
             "It is not reserved"],
            0,
            "Recognition in the scanner is what reserving means."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — statements.
# ---------------------------------------------------------------------------

_C13_S2 = _pstep(
    "statement", "Two kinds of statement",
    "`Stmt`, and `parseStatement`: `let NAME = EXPR`, or just an expression.",
    """
```ts
type LetStmt = { kind: "let"; name: string; value: Expr };
type ExprStmt = { kind: "expr"; expr: Expr };
type Stmt = LetStmt | ExprStmt;
```

The grammar gains a rule above `expr`:

```
statement  =  "let" name "=" expr  |  expr
```

A statement starting with `let` is a binding; anything else is an expression
standing on its own. One peek decides which:

```ts
function parseStatement(p: Parser): StmtResult {
  if (peek(p).kind !== "let") {
    const e = parseExpr(p);
    if (!e.ok) {
      return e;
    }
    return { ok: true, stmt: { kind: "expr", expr: e.expr } };
  }
  advance(p);
  const name = advance(p);
  if (name.kind !== "ident") {
    return expected("a name", name);
  }
  const eq = advance(p);
  if (eq.kind !== "equals") {
    return expected("'='", eq);
  }
  const value = parseExpr(p);
  …
}
```

After `let`, the parser knows exactly what must come next — a name, then `=` —
so it uses module 8's `expected`:

```
let = 4       error: expected a name but found '='
let x 4       error: expected '=' but found '4'
```

`"a name"` has no quotes, because it describes a *kind* of thing rather than
naming a particular token. That is why `expected` takes its first argument
already quoted.

### Why a statement is not an expression

`let x = 4` could have been an expression whose value is 4. Then `1 + let x = 4`
would be legal, and `(let x = 4) * x` would depend on evaluation order to mean
anything. Keeping bindings at statement level means a binding can only happen
*between* expressions, never in the middle of one.
""",
    """
```bash
$ echo 'let = 4' | node calc.ts
error: expected a name but found '='
$ echo 'let x 4' | node calc.ts
error: expected '=' but found '4'
```

The parser knows what it wanted after `let`, and says so.
""",
    pitfalls=[
        "Parsing `let` inside `parsePrimary`, as an expression. Then `1 + let x = 4` parses.",
        "`unexpectedToken` after `let`. `unexpected '='` is true; `expected a name but found '='` says what would have fixed it.",
        "Storing the name token in the statement instead of the name string. The evaluator only needs the text.",
        "Forgetting to advance past `let` before reading the name. The name check then sees the `let` itself.",
    ],
    warmup=[
        _pq("What does `let x = 4 x` report?",
            ["`error: unexpected 'x'` — the statement is complete after `4`, and a second `x` is neither `;` nor the end",
             "`error: expected ';'`",
             "`4`",
             "`error: expected a name but found 'x'`"],
            0,
            "The statement parses; what follows it does not fit. That is step 3's "
            "check."),
    ],
    exercises=[
        _pex("calc-m13-statement-1", "After `let`, a name",
             "In `parseStatement`, after taking the `let`, take the next token "
             "and insist it is a name.",
             _C13_FULL,
             '  const name = advance(p);\n  if (name.kind !== "ident") {\n    return expected("a name", name);\n  }',
             _C13_TESTS,
             ["`advance` to take it.",
              "A name is an `ident` token.",
              "If it is not, `expected(\"a name\", name)` — no quotes around `a name`."]),
        _pex("calc-m13-statement-2", "The shape of a statement",
             "Declare `Stmt`: a `let` binding a name to an expression, or a bare "
             "expression.",
             _C13_FULL,
             "type Stmt = LetStmt | ExprStmt;",
             _C13_TESTS,
             ["The two member types are declared just above.",
              "A union of them.",
              "`type Stmt = LetStmt | ExprStmt;`"]),
    ],
    quiz=[
        _pq("Why is `let` a statement rather than an expression with a value?",
            ["So a binding can only happen between expressions — never in the middle of one, where evaluation order would decide what it means",
             "Because `let` has no value",
             "Because the parser cannot parse it as an expression",
             "No reason"],
            0,
            "A deliberate limit that keeps programs readable."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — a program is a list.
# ---------------------------------------------------------------------------

_C13_S3 = _pstep(
    "program", "A program is a list",
    "`parseProgram`: statements separated by `;`, a trailing `;` allowed, and the end of the input to finish.",
    """
```
program  =  statement ( ";" statement )* ";"?
```

One or more statements, `;` between them, and optionally one more `;` at the
end. As code, a loop that parses a statement, then looks at what follows:

```ts
function parseProgram(tokens: Token[]): ProgramResult {
  const p: Parser = { tokens: tokens, pos: 0 };
  const program: Stmt[] = [];
  while (true) {
    const s = parseStatement(p);
    if (!s.ok) {
      return s;
    }
    program.push(s.stmt);
    const t = advance(p);
    if (t.kind === "eof") {
      return { ok: true, program: program };
    }
    if (t.kind !== "semi") {
      return unexpectedToken(t);
    }
    if (peek(p).kind === "eof") {
      return { ok: true, program: program };
    }
  }
}
```

After each statement, exactly three things can happen:

| Next token | Means |
|---|---|
| `eof` | the program is finished |
| `;` followed by `eof` | finished, with a trailing `;` |
| `;` followed by anything else | another statement is coming — go round again |
| anything else | leftovers: `unexpected …`, module 6's end check in a new place |

### This replaces `parse`

Module 6's `parse` checked for `eof` after one expression. `parseProgram` does
the same after each statement, and allows a `;` in between. It is the new entry
point to the parser, and `run` is the only thing that changes to call it.

### Five result types

`ScanResult`, `ParseResult`, `StmtResult`, `ProgramResult`, `EvalResult` — all
the same shape, all ending in `| Failure`. That is a lot of near-identical types,
and the pressure is real: a single generic `Result<T>` would replace them all.
It is in the stretch list. Noticing the pattern is the lesson; this project keeps
the descriptive field names (`tokens`, `expr`, `program`) for now.
""",
    """
```bash
$ echo '1; 2; 3' | node calc.ts
3
$ echo 'let x = 1;' | node calc.ts
1
$ echo '1 + 2;;' | node calc.ts
error: unexpected ';'
```

A trailing `;` is fine. Two in a row is an empty statement, which the language
does not have.
""",
    pitfalls=[
        "No trailing-`;` check: `let x = 1;` fails with `unexpected end of input`, because a statement was expected after the `;`.",
        "Allowing empty statements by skipping `;` in a loop. `;;;` then becomes a program with no statements — and no value.",
        "Checking for `eof` only at the top of the loop. An empty input then parses to an empty program instead of failing at its first primary.",
        "Keeping the old `parse` alongside. One entry point per stage; two means someone will call the wrong one.",
    ],
    warmup=[
        _pq("After a statement, the next token is `;` and the one after it is `eof`. What happens?",
            ["The program is complete — a trailing `;` is allowed",
             "`error: unexpected end of input`",
             "`error: unexpected ';'`",
             "Another statement is parsed"],
            0,
            "Many languages allow it; this one does too, on purpose."),
    ],
    exercises=[
        _pfix("calc-m13-program-fix1", "A semicolon at the end",
              "`let x = 1;` says `error: unexpected end of input`. The same "
              "program without its final `;` works.",
              _c13(program=_C13_PARSE_PROGRAM.replace(
                  '    if (peek(p).kind === "eof") {\n      return { ok: true, program: program };\n    }\n', "")),
              _C13_FULL,
              _C13_TESTS,
              ["After a `;`, what does the loop assume comes next?",
               "It always parses another statement — even when the input has ended.",
               "After a `;`, peek: if it is `eof`, the program is finished."],
              difficulty="Easy"),
        _pch("calc-m13-program-loop", "Statements until the end", "Medium",
             "Write `parseProgram`: statements separated by `;`, an optional "
             "trailing `;`, and leftovers reported as unexpected.",
             _C13_FULL,
             "function parseProgram" + _C13_PARSE_PROGRAM.split("\n\nfunction parseProgram")[1].rstrip("\n"),
             _C13_TESTS,
             ["A `Parser` at position 0, an empty `Stmt[]`, and `while (true)`.",
              "Parse a statement and push it. Then `advance`.",
              "`eof` → done. Not `;` → `unexpectedToken`. `;` then `eof` → done."]),
    ],
    quiz=[
        _pq("What does `;` alone report, and why?",
            ["`error: unexpected ';'` — a program must start with a statement, and a statement cannot start with `;`",
             "An empty program",
             "`0`",
             "`error: unexpected end of input`"],
            0,
            "The first primary fails, as it would for any expression."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — what a program's value is.
# ---------------------------------------------------------------------------

_C13_S4 = _pstep(
    "value", "What a program's value is",
    "`execute` and `runProgram`: statements in order, one environment, the last value wins.",
    """
Running a statement is a switch on its kind — with module 10's check, because
`Stmt` is a union and will grow:

```ts
function execute(s: Stmt, env: Env): EvalResult {
  switch (s.kind) {
    case "let": {
      const result = evaluate(s.value, env);
      if (!result.ok) {
        return result;
      }
      env.set(s.name, result.value);
      return result;
    }
    case "expr":
      return evaluate(s.expr, env);
    default: {
      const impossible: never = s;
      return impossible;
    }
  }
}
```

A `let` evaluates its expression and binds the name — **only if the evaluation
succeeded**, so a failing `let` leaves the environment untouched. Its value is
the value it bound. An expression statement is just its value.

Running a program runs its statements in order and keeps the last value:

```ts
function runProgram(program: Stmt[], env: Env): EvalResult {
  let last: EvalResult = { ok: false, error: "error: empty program" };
  for (const s of program) {
    last = execute(s, env);
    if (!last.ok) {
      return last;
    }
  }
  return last;
}
```

### The empty program

`parseProgram` never produces an empty list — every program has at least one
statement, or it failed to parse. But `Stmt[]` allows an empty list, and
`runProgram` has to say what one would mean. So `last` starts as a failure with a
message no user will ever see. That gap — between what the parser guarantees and
what the type says — is real, and closing it would take a type for "a list with
at least one element". Knowing where your types are looser than your program is
half of using them well.

### The environment starts empty

Module 12's `day`, `week` and `dozen` are gone. `run` gets a fresh `new Map()`,
and everything in it was put there by a `let` in the program. The language no
longer needs anything from outside it.
""",
    """
```bash
$ echo 'let x = 4; x * x' | node calc.ts
16
$ echo 'let x = 2; let y = x * 3; y + x' | node calc.ts
8
$ echo 'x; let x = 1' | node calc.ts
error: undefined variable 'x'
```

The last one fails because statements run in order: `x` is read before the
`let` that would have defined it.
""",
    pitfalls=[
        "Binding before checking: `env.set(s.name, …)` on a failed result. It does not compile — `result.value` does not exist yet — which is the result type earning its keep.",
        "Forgetting `env.set`. Every `let` evaluates and throws the value away; the next statement's use of the name is undefined.",
        "Returning the first statement's value. A program's value is its LAST statement's.",
        "Parsing and running statement by statement. Then `1; 1 +` runs the `1` before discovering the syntax error — output, then an error, for one program.",
    ],
    warmup=[
        _pq("What does `let x = 1; let x = x + 1; x` print?",
            ["`2` — the second `let` reads the old `x`, then replaces it",
             "`1`",
             "An error: `x` is already defined",
             "`3`"],
            0,
            "The right-hand side is evaluated before the name is rebound."),
    ],
    exercises=[
        _pex("calc-m13-value-1", "Bind the name",
             "In `execute`'s `let` case, once the value has been evaluated "
             "successfully, bind the name to it.",
             _C13_FULL,
             "      env.set(s.name, result.value);",
             _C13_TESTS,
             ["The environment is a Map.",
              "The name is `s.name`; the value is the success's `value`.",
              "`env.set(s.name, result.value);`"]),
        _pfix("calc-m13-value-fix1", "A `let` that forgets",
              "`let x = 4` prints `4`. `let x = 4; x * x` says `error: undefined "
              "variable 'x'`. The binding is evaluated and then goes nowhere.",
              _c13(execute=_C13_EXECUTE.replace("      env.set(s.name, result.value);\n", "")),
              _C13_FULL,
              _C13_TESTS,
              ["Where does a `let` statement put its value?",
               "It evaluates it, and returns it — and nothing else.",
               "`env.set(s.name, result.value);` before returning."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does `runProgram` start `last` as a failure?",
            ["An empty `Stmt[]` has no value; the parser never produces one, but the type allows it, so it must mean something",
             "Because every program fails first",
             "To report syntax errors",
             "It starts as 0"],
            0,
            "The type is looser than the parser's guarantee. Say what the gap "
            "means."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C13_FINAL = _pch(
    "calc-m13-build", "Module 13 build — a program", "Hard",
    "Write the statement parser, between `parseSum` and the evaluator:\n\n"
    "* `StmtResult` and `parseStatement` — `let NAME = EXPR` or an expression, "
    "with `expected a name` and `expected '='`\n"
    "* `ProgramResult` and `parseProgram` — statements separated by `;`, a "
    "trailing `;` allowed, leftovers reported as unexpected\n\n"
    "`execute`, `runProgram` and `run` are given. The tests include "
    "`let x = 1;`, `1 + 2;;` and `let let = 1`.",
    _C13_FULL,
    _cjoin(_C13_PARSE_STMT, _C13_PARSE_PROGRAM).rstrip("\n"),
    _C13_TESTS,
    ["`parseStatement`: peek for `let`; otherwise parse an expression statement.",
     "After `let`: a name (`ident`), then `=` (`equals`), then an expression.",
     "`parseProgram`: `while (true)` — statement, push, then `eof`, `;`, or unexpected.",
     "After a `;`, peek: `eof` means the program ended with a trailing `;`."],
)

_CALC_MODULES.append(_pmod(
    key="calc-statements", number=13, phase="lang",
    title="Statements, and a program",
    what="many statements separated by `;`, and what a program's value is",
    goal="Run `let x = 4; x * x` as one program.",
    why=_C13_WHY,
    est_minutes=45,
    builds_on=["calc-vars"],
    concepts=["statements vs expressions", "keywords", "reserved words",
              "program as a list", "separators", "sequential execution",
              "a program's value", "types looser than guarantees"],
    deliverable="`echo 'let x = 4; x * x' | node calc.ts` prints `16` — a program "
                "is a sequence of statements, run in order against an environment "
                "it fills itself.",
    objectives=[
        "Recognise a keyword after scanning a whole word, and say why that makes it reserved",
        "Declare a statement union and parse `let NAME = EXPR` with `expected` messages",
        "Parse a `;`-separated program with an optional trailing `;`",
        "Run statements in order against one environment, binding only on success",
        "State what a program's value is, and what an empty program would mean",
        "Say what changed about the parser's entry point, and why only `run` noticed",
    ],
    brief=_C13_BRIEF,
    syntax=_C13_SYNTAX,
    steps=[_C13_S1, _C13_S2, _C13_S3, _C13_S4],
    final_build=_C13_FINAL,
    acceptance=[
        "`echo 'let x = 4; x * x' | node calc.ts` prints `16`.",
        "`echo 'let x = 4' | node calc.ts` prints `4`.",
        "`echo '1; 2; 3' | node calc.ts` prints `3`.",
        "`echo 'let x = 1;' | node calc.ts` prints `1` — a trailing `;` is allowed.",
        "`echo 'x; let x = 1' | node calc.ts` prints `error: undefined variable 'x'`.",
        "`echo 'let let = 1' | node calc.ts` prints `error: expected a name but found 'let'`.",
        "`echo 'week' | node calc.ts` is now undefined — the environment starts empty.",
    ],
    manual_test="""
```bash
echo 'let x = 4; x * x'                   | node calc.ts     # 16
echo 'let x = 2; let y = x * 3; y + x'    | node calc.ts     # 8
echo 'let x = 1; let x = x + 1; x'        | node calc.ts     # 2
echo 'let x = 1;'                         | node calc.ts     # 1
echo 'x; let x = 1'                       | node calc.ts     # undefined variable 'x'
echo 'let = 4'                            | node calc.ts     # expected a name but found '='
echo 'let x 4'                            | node calc.ts     # expected '=' but found '4'
echo '1 + 2;;'                            | node calc.ts     # unexpected ';'
```

One more to think about: `echo 'let a = 1; a / 0' | node calc.ts`. It prints the
division error. Was `a` bound? (Yes — the first statement ran and succeeded
before the second failed.) Nothing can observe that yet. Module 18's REPL keeps
one environment across many lines, and there it will matter; decide now whether
you think it is right.
""",
    reference="""// calc.ts — module 13
//
// A program is a list of statements separated by `;` (a trailing `;` is fine):
//
//   program    = statement ( ";" statement )* ";"?
//   statement  = "let" name "=" expr | expr
//
// Statements run in order against one environment, which starts empty. A let
// binds only if its expression evaluated; its value is the value it bound. A
// program's value is its last statement's. `let` is a keyword, so it is reserved.
""" + _C13_FULL,
    stretch=[
        "Replace the five result types with one: `type Result<T> = { ok: true; value: T } | Failure`. Every `.tokens`, `.expr`, `.stmt` and `.program` becomes `.value` — decide whether you miss the names.",
        "Make `let` refuse to rebind a name that already exists: `error: 'x' is already defined`. Then write a program that needs rebinding, and decide which rule is better.",
        "Add a `print EXPR` statement that outputs a value as it runs, so a program can show more than its last value. Where does the output go — straight to `console.log`, or back through `run`?",
        "Type a program as non-empty: `type Program = [Stmt, ...Stmt[]]`. Find out what `parseProgram` must change to produce one, and whether `runProgram` still needs its placeholder failure.",
    ],
    glossary=[
        _pgloss("statement", "A unit of a program that does something — binds a name, or evaluates an expression — rather than being a value inside one."),
        _pgloss("keyword", "A word with a fixed meaning in the language, recognised by the scanner. `let`."),
        _pgloss("reserved word", "A word that cannot be used as a name, because the scanner turns it into its own token."),
        _pgloss("program", "Here, a non-empty list of statements run in order. Its value is its last statement's."),
        _pgloss("binding", "The association of a name with a value in an environment. `let x = 4` creates one."),
    ],
    cheatsheet="""
```
program    = statement ( ";" statement )* ";"?
statement  = "let" name "=" expr  |  expr
```

```ts
type Stmt = { kind: "let"; name: string; value: Expr } | { kind: "expr"; expr: Expr };

// scanner: the whole word, THEN the keyword check
const word = src.slice(start, i);
if (word === "let") { tokens.push(letToken()); } else { tokens.push(identToken(word)); }

// execute: bind only after a successful evaluation
case "let": {
  const result = evaluate(s.value, env);
  if (!result.ok) { return result; }
  env.set(s.name, result.value);
  return result;                       // a let's value is what it bound
}
```

| Input | Output |
|---|---|
| `let x = 4; x * x` | `16` |
| `let x = 4` | `4` |
| `1; 2; 3` | `3` |
| `let x = 1;` | `1` |
| `x; let x = 1` | `error: undefined variable 'x'` |
| `let x 4` | `error: expected '=' but found '4'` |
| `1 + 2;;` | `error: unexpected ';'` |

| Symptom | Cause |
|---|---|
| `let x = 4` → `unexpected 'x'` | the scanner never produces a `let` token |
| trailing `;` → `unexpected end of input` | no `eof` check after `;` |
| `let x = 4; x` → undefined | `execute` does not `env.set` |
""",
    self_check=[
        "Can you say what separates a statement from an expression, with an example of each?",
        "Can you explain why `letter` is a name and `let` is not?",
        "Can you write the grammar for a program, including the trailing `;`?",
        "Can you give the value of `let x = 2; let y = x * 3; y + x` and trace how it is reached?",
        "Can you explain why `runProgram` starts from a failure it will never return?",
    ],
    review=[
        _pq("What does the parser's entry point return after this module?",
            ["A `ProgramResult` — a list of statements, or a failure",
             "A `ParseResult` with one `Expr`",
             "A number",
             "A list of tokens"],
            0,
            "The contract change. Only `run` had to notice."),
        _pq("What is the value of the program `let x = 4`?",
            ["`4` — a `let`'s value is the value it bound, and a program's value is its last statement's",
             "Nothing; `let` has no value",
             "`undefined`",
             "`0`"],
            0,
            "Decided in step 4."),
        _pq("`let a = 1; b` — what is reported?",
            ["`error: undefined variable 'b'`",
             "`1`",
             "`error: unexpected 'b'`",
             "`error: expected ';'`"],
            0,
            "It parses; `b` just has no value."),
        _pq("Why does `let x = 1; let x = x + 1; x` print 2?",
            ["The right-hand side is evaluated with the old `x`, then `set` replaces it",
             "Because `let` adds to the existing value",
             "Because the second `let` is ignored",
             "It prints 1"],
            0,
            "Evaluate, then bind."),
        _pq("A failing `let` — `let x = 1 / 0` — does it bind `x`?",
            ["No — `env.set` only runs after a successful evaluation, and the compiler will not let it run before",
             "Yes, to Infinity",
             "Yes, to 0",
             "Yes, to undefined"],
            0,
            "The result type decides the order."),
    ],
    milestone="`calc.ts` runs programs. `let` writes into an environment that starts "
              "empty, `;` separates statements that run in order, and a program's "
              "value is its last statement's. Expressions and programs are different "
              "things now — and the language needs nothing from outside itself.",
))
