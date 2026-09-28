# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 16 — Line and column on every token.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. The program is written out IN FULL here rather than
# derived by string replacement: the retrofit touches nearly every part, and a
# reader of this file should be able to see the whole of it.
#
# THE RETROFIT MODULE, AND DELIBERATELY SO. Module 6 chose to report parse
# errors without a column and said module 16 would pay for it. Here is the bill:
#
#   * `type Pos = { line: number; col: number }` on EVERY token and EVERY node.
#     Because tokens have only ever been built by module 1's factories, the
#     change is: each factory gains a `pos` parameter, and each call site passes
#     one. Step 1 says that out loud — the clearest payoff in the project for a
#     decision that looked like ceremony at the time.
#   * The scanner tracks `line` and `lineStart`; `\n` starts a new line and `\r`
#     is whitespace, so a program can span lines (and a Windows file works).
#   * Errors stop being strings. `CalcError = { message; pos }`, built by
#     `fail(message, pos)`, and turned into text in ONE place, `formatError`:
#         error: <message> at <line>:<col>
#     Module 4's scan-error text is unchanged; every other error GAINS ` at L:C`.
#     That extension of the contract was promised in module 6.
#
# WHERE EACH ERROR POINTS (decided here, relied on by module 17's caret):
#   token errors → the token; eof → just past the last character;
#   division by zero, overflow, cannot apply/compare → the OPERATOR;
#   undefined variable → the name; a too-large literal → the literal;
#   negation of a boolean → the `-`; a non-boolean condition → the `if`.
#
# `peek`'s unreachable fallback now needs a position for a token that cannot
# exist. It gets `{ line: 0, col: 0 }` — a position no source has — and the step
# says module 17 has a better tool for "cannot happen".
# ---------------------------------------------------------------------------

_C16_TOKENS = """type Pos = { line: number; col: number };

type Op = "+" | "-" | "*" | "/" | "<" | ">" | "==";

type NumberToken = { kind: "number"; value: number; pos: Pos };
type BoolToken = { kind: "bool"; value: boolean; pos: Pos };
type OpToken = { kind: "op"; op: Op; pos: Pos };
type IdentToken = { kind: "ident"; name: string; pos: Pos };
type LetToken = { kind: "let"; pos: Pos };
type EqualsToken = { kind: "equals"; pos: Pos };
type SemiToken = { kind: "semi"; pos: Pos };
type IfToken = { kind: "if"; pos: Pos };
type ThenToken = { kind: "then"; pos: Pos };
type ElseToken = { kind: "else"; pos: Pos };
type LParenToken = { kind: "lparen"; pos: Pos };
type RParenToken = { kind: "rparen"; pos: Pos };
type EofToken = { kind: "eof"; pos: Pos };

type Token =
  | NumberToken
  | BoolToken
  | OpToken
  | IdentToken
  | LetToken
  | EqualsToken
  | SemiToken
  | IfToken
  | ThenToken
  | ElseToken
  | LParenToken
  | RParenToken
  | EofToken;

function numberToken(value: number, pos: Pos): NumberToken {
  return { kind: "number", value: value, pos: pos };
}

function boolToken(value: boolean, pos: Pos): BoolToken {
  return { kind: "bool", value: value, pos: pos };
}

function opToken(op: Op, pos: Pos): OpToken {
  return { kind: "op", op: op, pos: pos };
}

function identToken(name: string, pos: Pos): IdentToken {
  return { kind: "ident", name: name, pos: pos };
}

function letToken(pos: Pos): LetToken {
  return { kind: "let", pos: pos };
}

function equalsToken(pos: Pos): EqualsToken {
  return { kind: "equals", pos: pos };
}

function semiToken(pos: Pos): SemiToken {
  return { kind: "semi", pos: pos };
}

function ifToken(pos: Pos): IfToken {
  return { kind: "if", pos: pos };
}

function thenToken(pos: Pos): ThenToken {
  return { kind: "then", pos: pos };
}

function elseToken(pos: Pos): ElseToken {
  return { kind: "else", pos: pos };
}

function lparenToken(pos: Pos): LParenToken {
  return { kind: "lparen", pos: pos };
}

function rparenToken(pos: Pos): RParenToken {
  return { kind: "rparen", pos: pos };
}

function eofToken(pos: Pos): EofToken {
  return { kind: "eof", pos: pos };
}
"""

_C16_ERRORS = """type CalcError = { message: string; pos: Pos };
type Failure = { ok: false; error: CalcError };
type ScanResult = { ok: true; tokens: Token[] } | Failure;

function fail(message: string, pos: Pos): Failure {
  return { ok: false, error: { message: message, pos: pos } };
}

function formatError(err: CalcError): string {
  return `error: ${err.message} at ${err.pos.line}:${err.pos.col}`;
}
"""

_C16_NEWLINE = """    if (ch === "\\n") {
      i = i + 1;
      line = line + 1;
      lineStart = i;
    } else if (ch === " " || ch === "\\r") {
"""

_C16_SCAN = """const DIGITS = "0123456789";

function isDigit(ch: string): boolean {
  return DIGITS.indexOf(ch) !== -1;
}

const LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_";

function isLetter(ch: string): boolean {
  return LETTERS.indexOf(ch) !== -1;
}

function scan(src: string): ScanResult {
  const tokens: Token[] = [];
  let i = 0;
  let line = 1;
  let lineStart = 0;
  while (i < src.length) {
    const ch = src.charAt(i);
    const pos: Pos = { line: line, col: i - lineStart + 1 };
""" + _C16_NEWLINE + """      i = i + 1;
    } else if (isDigit(ch)) {
      const start = i;
      while (i < src.length && isDigit(src.charAt(i))) {
        i = i + 1;
      }
      tokens.push(numberToken(Number(src.slice(start, i)), pos));
    } else if (ch === "+" || ch === "-" || ch === "*" || ch === "/" || ch === "<" || ch === ">") {
      tokens.push(opToken(ch, pos));
      i = i + 1;
    } else if (ch === "(") {
      tokens.push(lparenToken(pos));
      i = i + 1;
    } else if (ch === ")") {
      tokens.push(rparenToken(pos));
      i = i + 1;
    } else if (isLetter(ch)) {
      const start = i;
      while (i < src.length && (isLetter(src.charAt(i)) || isDigit(src.charAt(i)))) {
        i = i + 1;
      }
      const word = src.slice(start, i);
      if (word === "let") {
        tokens.push(letToken(pos));
      } else if (word === "true" || word === "false") {
        tokens.push(boolToken(word === "true", pos));
      } else if (word === "if") {
        tokens.push(ifToken(pos));
      } else if (word === "then") {
        tokens.push(thenToken(pos));
      } else if (word === "else") {
        tokens.push(elseToken(pos));
      } else {
        tokens.push(identToken(word, pos));
      }
    } else if (ch === "=") {
      if (src.charAt(i + 1) === "=") {
        tokens.push(opToken("==", pos));
        i = i + 2;
      } else {
        tokens.push(equalsToken(pos));
        i = i + 1;
      }
    } else if (ch === ";") {
      tokens.push(semiToken(pos));
      i = i + 1;
    } else {
      return fail(`unexpected '${ch}'`, pos);
    }
  }
  tokens.push(eofToken({ line: line, col: i - lineStart + 1 }));
  return { ok: true, tokens: tokens };
}
"""

_C16_TREE = """type NumLit = { kind: "num"; value: number; pos: Pos };
type BoolLit = { kind: "bool"; value: boolean; pos: Pos };
type Var = { kind: "var"; name: string; pos: Pos };
type Neg = { kind: "neg"; operand: Expr; pos: Pos };
type If = { kind: "if"; cond: Expr; whenTrue: Expr; whenFalse: Expr; pos: Pos };
type Binary = { kind: "binary"; op: Op; left: Expr; right: Expr; pos: Pos };

type Expr = NumLit | BoolLit | Var | Neg | If | Binary;

function num(value: number, pos: Pos): NumLit {
  return { kind: "num", value: value, pos: pos };
}

function boolLit(value: boolean, pos: Pos): BoolLit {
  return { kind: "bool", value: value, pos: pos };
}

function variable(name: string, pos: Pos): Var {
  return { kind: "var", name: name, pos: pos };
}

function neg(operand: Expr, pos: Pos): Neg {
  return { kind: "neg", operand: operand, pos: pos };
}

function ifExpr(cond: Expr, whenTrue: Expr, whenFalse: Expr, pos: Pos): If {
  return { kind: "if", cond: cond, whenTrue: whenTrue, whenFalse: whenFalse, pos: pos };
}

function binary(op: Op, left: Expr, right: Expr, pos: Pos): Binary {
  return { kind: "binary", op: op, left: left, right: right, pos: pos };
}
"""

_C16_STATE = """type Parser = { tokens: Token[]; pos: number };

function peek(p: Parser): Token {
  const t = p.tokens[p.pos];
  if (t === undefined) {
    return eofToken({ line: 0, col: 0 });
  }
  return t;
}

function advance(p: Parser): Token {
  const t = peek(p);
  if (t.kind !== "eof") {
    p.pos = p.pos + 1;
  }
  return t;
}
"""

_C16_DESCRIBE = _C15_DESCRIBE.split("\n\nfunction unexpectedToken")[0] + """

function unexpectedToken(t: Token): Failure {
  return fail(`unexpected ${describe(t)}`, t.pos);
}

function expected(what: string, t: Token): Failure {
  return fail(`expected ${what} but found ${describe(t)}`, t.pos);
}
"""

_C16_PRIMARY = _C15_PRIMARY \
    .replace("expr: num(t.value) }", "expr: num(t.value, t.pos) }") \
    .replace("expr: boolLit(t.value) }", "expr: boolLit(t.value, t.pos) }") \
    .replace("expr: variable(t.name) }", "expr: variable(t.name, t.pos) }") \
    .replace("ifExpr(cond.expr, whenTrue.expr, whenFalse.expr)", "ifExpr(cond.expr, whenTrue.expr, whenFalse.expr, t.pos)")

_C16_UNARY = _C8_UNARY.replace("neg(operand.expr)", "neg(operand.expr, t.pos)")


def _c16_level(src):
    return src.replace("binary(t.op, left, right.expr)", "binary(t.op, left, right.expr, t.pos)")


_C16_PRODUCT = _c16_level(_C8_PRODUCT)
_C16_SUM = _c16_level(_C7_SUM)
_C16_COMPARISON = _c16_level(_C14_COMPARISON)

_C16_RESULT = """type Value = number | boolean;

type EvalResult = { ok: true; value: Value } | Failure;

function checked(value: number, pos: Pos): EvalResult {
  if (!Number.isFinite(value)) {
    return fail("number too large", pos);
  }
  return { ok: true, value: value };
}
"""

_C16_EVAL = """function evaluate(e: Expr, env: Env): EvalResult {
  switch (e.kind) {
    case "num":
      return checked(e.value, e.pos);
    case "bool":
      return { ok: true, value: e.value };
    case "var": {
      const value = env.get(e.name);
      if (value === undefined) {
        return fail(`undefined variable '${e.name}'`, e.pos);
      }
      return { ok: true, value: value };
    }
    case "neg": {
      const operand = evaluate(e.operand, env);
      if (!operand.ok) {
        return operand;
      }
      if (typeof operand.value !== "number") {
        return fail("cannot apply '-' to a boolean", e.pos);
      }
      return { ok: true, value: -operand.value };
    }
    case "if": {
      const cond = evaluate(e.cond, env);
      if (!cond.ok) {
        return cond;
      }
      if (typeof cond.value !== "boolean") {
        return fail("if condition must be a boolean", e.pos);
      }
      if (cond.value) {
        return evaluate(e.whenTrue, env);
      }
      return evaluate(e.whenFalse, env);
    }
    case "binary": {
      const left = evaluate(e.left, env);
      if (!left.ok) {
        return left;
      }
      const right = evaluate(e.right, env);
      if (!right.ok) {
        return right;
      }
      return apply(e.op, left.value, right.value, e.pos);
    }
    default: {
      const impossible: never = e;
      return impossible;
    }
  }
}
"""

_C16_APPLY = """function apply(op: Op, left: Value, right: Value, pos: Pos): EvalResult {
  if (op === "==") {
    if (typeof left !== typeof right) {
      return fail(`cannot compare a ${typeof left} with a ${typeof right}`, pos);
    }
    return { ok: true, value: left === right };
  }
  if (typeof left !== "number" || typeof right !== "number") {
    return fail(`cannot apply '${op}' to a boolean`, pos);
  }
  switch (op) {
    case "+":
      return checked(left + right, pos);
    case "-":
      return checked(left - right, pos);
    case "*":
      return checked(left * right, pos);
    case "/":
      if (right === 0) {
        return fail("division by zero", pos);
      }
      return checked(left / right, pos);
    case "<":
      return { ok: true, value: left < right };
    case ">":
      return { ok: true, value: left > right };
    default: {
      const impossible: never = op;
      return impossible;
    }
  }
}
"""

_C16_EXECUTE = _C13_EXECUTE.replace(
    '  let last: EvalResult = { ok: false, error: "error: empty program" };',
    '  let last: EvalResult = fail("empty program", { line: 1, col: 1 });', 1)

_C16_RUN_FN = """function run(src: string, env: Env): string {
  const scanned = scan(src);
  if (!scanned.ok) {
    return formatError(scanned.error);
  }
  const parsed = parseProgram(scanned.tokens);
  if (!parsed.ok) {
    return formatError(parsed.error);
  }
  const result = runProgram(parsed.program, env);
  if (!result.ok) {
    return formatError(result.error);
  }
  return `${result.value}`;
}
"""


def _c16(tokens=_C16_TOKENS, errors=_C16_ERRORS, scan=_C16_SCAN, tree=_C16_TREE,
         describe=_C16_DESCRIBE, primary=_C16_PRIMARY, unary=_C16_UNARY,
         product=_C16_PRODUCT, evaluate=_C16_EVAL, apply=_C16_APPLY, run=_C16_RUN_FN):
    return _stdin(_cjoin(tokens, errors, scan, tree, _C13_STMTS, _C16_STATE, describe,
                         primary, unary, product, _C16_SUM, _C16_COMPARISON,
                         _C13_PARSE_STMT, _C13_PARSE_PROGRAM, _C16_RESULT, _C14_ENV,
                         evaluate, apply, _C16_EXECUTE, run, _C13_MAIN))


_C16_FULL = _c16()

_C16_INPUTS = ["1 + )", "1 $ 2", "  1 $ 2", "1 +", "(1 + 2", "let x 4",
               "let x = 4;\nx * y", "let a = 1;\nlet b = 0;\na / b", "1 + 2 / 0",
               "true * 2", "1 == true", "  -true", "if 1 then 2 else 3", "x",
               _C11_HUGE, _C11_BIG + " * 10000000000", "1\n+", "",
               "let x = 4;\nx * x", "let x = 1;\r\nx + 1", "1 + 2 * 3",
               "if false then 1 / 0 else 2"]
_C16_TESTS = _ctests(16, _C16_INPUTS)

_C16_WHY = (
    "`echo '1 + )' | node calc.ts` says `error: unexpected ')'`, and for a line "
    "that short, that is enough. For `let total = price * (1 + rate; total` it is "
    "not: which bracket, which line, which character? Module 6 decided to report "
    "*what* without *where*, because tokens did not carry positions, and said this "
    "module would pay for it. Here is the bill. Every token and every node learns "
    "where it came from, every error carries a position, and one function turns "
    "an error into text. It sounds like a rewrite. It is not — and the reason it "
    "is not is a decision module 1 made about factories, which finally shows what "
    "it was for."
)

_C16_BRIEF = """
### The whole module in one line

Every token and every node carries `{ line, col }`, so every error — scan,
parse or evaluate — ends ` at 2:5`, pointing at the character responsible.

### The bill from module 6

```
module 6–15:   error: unexpected ')'
module 16:     error: unexpected ')' at 1:5
```

Module 6 chose not to thread positions through the parser, and said module 16
would add them to tokens instead. That choice is due.

### Why it is a small change

Module 1 insisted that tokens are built by **factories** — `numberToken(7)`,
never `{ kind: "number", value: 7 }` written out by hand. It looked like
ceremony. Here is what it bought: to give every token a position, you change the
factories and the places that call them. There is no hand-written token object
anywhere else in `calc.ts` to hunt for. Module 5 did the same for nodes.

```ts
type Pos = { line: number; col: number };
type NumberToken = { kind: "number"; value: number; pos: Pos };

function numberToken(value: number, pos: Pos): NumberToken {
  return { kind: "number", value: value, pos: pos };
}
```

And the compiler finds every call site for you — each one is now missing an
argument.

### Programs with more than one line

A position is only interesting if there is more than one line. So the scanner
now treats a newline as whitespace that starts a new line, and `\\r` as plain
whitespace (so a file saved on Windows works):

```
$ printf 'let x = 4;\\nx * y' | node calc.ts
error: undefined variable 'y' at 2:5
```

### Errors become data

```ts
type CalcError = { message: string; pos: Pos };
type Failure = { ok: false; error: CalcError };
```

An error is no longer a finished sentence — it is a message and a place, and ONE
function, `formatError`, turns it into `error: … at L:C`. Module 17 needs the
place as data, not text, to draw a caret under the right character.
"""

_C16_SYNTAX = [
    _syn(
        "type Pos = { line: number; col: number };",
        "A place in the source: a line and a column, both counting from 1.",
        "",
        "Two numbers, not an index into the string. A person reading an error "
        "thinks in lines and columns, and so does every editor.",
    ),
    _syn(
        "function numberToken(value: number, pos: Pos): NumberToken { … }",
        "Every factory gains a `pos` parameter, and every token it builds carries "
        "it. The compiler then lists every call that is missing one.",
        """
tokens.push(numberToken(Number(text), pos));
tokens.push(eofToken({ line: line, col: i - lineStart + 1 }));
""",
        "An object literal `{ line: line, col: … }` can be passed straight to a "
        "`Pos` parameter.",
    ),
    _syn(
        "const pos: Pos = { line: line, col: i - lineStart + 1 };",
        "The position of the character at `i`: which line it is on, and how far "
        "it is from the start of that line.",
        "",
        "`lineStart` is the index where the current line began. Columns count from "
        "1, so the first character of a line is `i - lineStart + 1 = 1`.",
    ),
    _syn(
        "type CalcError = { message: string; pos: Pos };",
        "An error as data: what went wrong and where. Formatting it is a separate "
        "job.",
        """
function fail(message: string, pos: Pos): Failure {
  return { ok: false, error: { message: message, pos: pos } };
}
""",
        "A nested object literal — the `error` field of the failure is itself an "
        "object.",
    ),
    _syn(
        "`error: ${err.message} at ${err.pos.line}:${err.pos.col}`",
        "The one place an error becomes text. Module 4's format, now for every "
        "error in the program.",
        "",
        "",
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — the retrofit.
# ---------------------------------------------------------------------------

_C16_S1 = _pstep(
    "retrofit", "The retrofit",
    "`Pos` on every token and node — and why module 1's factories make it a small change.",
    """
```ts
type Pos = { line: number; col: number };
```

Every token type gains a field:

```ts
type NumberToken = { kind: "number"; value: number; pos: Pos };
type OpToken = { kind: "op"; op: Op; pos: Pos };
type EofToken = { kind: "eof"; pos: Pos };
…
```

Because **every** member of `Token` has `pos`, `t.pos` can be read on any token
without narrowing first — the compiler knows all thirteen kinds have it. That is
what lets one `unexpectedToken(t)` report any token's position.

### The part that matters: the factories

Module 1 was insistent. Build tokens with factories:

```ts
function numberToken(value: number, pos: Pos): NumberToken {
  return { kind: "number", value: value, pos: pos };
}
```

— never by writing `{ kind: "number", value: 7 }` inline. At the time that was a
rule with an argument but no evidence. Here is the evidence. Adding a field to
every token means:

1. change the thirteen factories, and
2. change every call to a factory.

That is **all**. And step 2 is found for you: add the parameter, compile, and
every call site is an error — `Expected 2 arguments, but got 1` — until it passes
a position. There is no hand-built token anywhere else in `calc.ts` that could
be missed, because there never was one.

Had tokens been written inline for fifteen modules, this module would be a
search through every file for every `kind:`, hoping to find them all. It is the
clearest payoff in the project for a decision that looked like ceremony.

### Nodes too

Module 5 made the same choice for nodes — `num`, `binary`, `neg` — and they get
the same retrofit. A node needs a position because evaluation errors happen at
nodes: `1 / 0` fails at the `/`, and only the `binary` node knows where that was.
""",
    """
```
$ npx tsc --noEmit --strict calc.ts
```

After changing the types and factories, every call site is a compile error until
it passes a position. Work through the list; when it is empty, the retrofit is
done.
""",
    pitfalls=[
        "Adding `pos?: Pos` as optional to make the errors go away. Then nothing forces anyone to pass one, and half the errors have no position.",
        "Storing a character index instead of a line and column. It is simpler to carry, and then every error needs the source again to work out where the index is.",
        "Giving only some token kinds a position. `t.pos` on a `Token` then needs narrowing first, and `unexpectedToken` cannot report every kind.",
    ],
    warmup=[
        _pq("After adding a `pos` parameter to every factory, how do you find the calls that need updating?",
            ["Compile — each call is now an error for a missing argument",
             "Search the file for `kind:`",
             "Run the tests",
             "They update themselves"],
            0,
            "The compiler hands you the list, because factories are the only way tokens are built."),
    ],
    exercises=[
        _pex("calc-m16-retrofit-1", "A factory that remembers",
             "Finish `opToken`: an operator token carrying its operator and its "
             "position.",
             _C16_FULL,
             '  return { kind: "op", op: op, pos: pos };',
             _C16_TESTS,
             ["Every token now has a `pos` field.",
              "`return { kind: \"op\", op: op, pos: pos };`"]),
        _pex("calc-m16-retrofit-2", "Where a sum happened",
             "In `parseSum`, the binary node records the position of its operator.",
             _C16_FULL,
             "    left = binary(t.op, left, right.expr, t.pos);\n    t = peek(p);\n  }\n  return { ok: true, expr: left };\n}\n\nfunction parseComparison",
             _C16_TESTS,
             ["`binary` takes a fourth argument now.",
              "The operator token is `t`, and it has a `pos`.",
              "`left = binary(t.op, left, right.expr, t.pos);`"]),
    ],
    quiz=[
        _pq("Why is adding positions a small change rather than a rewrite?",
            ["Tokens and nodes are only ever built by factories, so only the factories and their calls change",
             "Because positions are optional",
             "Because TypeScript adds them automatically",
             "It is a rewrite"],
            0,
            "Module 1's rule, paid out fifteen modules later."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — lines and columns in the scanner.
# ---------------------------------------------------------------------------

_C16_S2 = _pstep(
    "lines", "Lines and columns",
    "The scanner counts lines, remembers where each one started, and positions every token — including the end.",
    """
The scanner has had `i` — a position in the whole string — since module 2. A
line and column are worked out from it with two more variables:

```ts
let line = 1;
let lineStart = 0;          // index where the current line began
```

At the top of the loop, before anything is consumed, the current character's
position is:

```ts
const pos: Pos = { line: line, col: i - lineStart + 1 };
```

and a newline moves both:

```ts
if (ch === "\\n") {
  i = i + 1;
  line = line + 1;
  lineStart = i;
} else if (ch === " " || ch === "\\r") {
  i = i + 1;
}
```

After a `\\n`, the next line starts at the next index, so `lineStart = i` *after*
the increment. `\\r` is whitespace, because Windows ends lines with `\\r\\n` and a
program saved there should not fail on an invisible character.

### Every token gets the position it STARTED at

A number is several characters, but its position is its first. That is why
`pos` is computed at the top of the loop and passed to the factory at the end of
the branch: `numberToken(Number(src.slice(start, i)), pos)`.

### The end of the input

`eof` is not a character, but it needs a position — `1 +` fails *there*. It is
the column just past the last character, on the last line:

```ts
tokens.push(eofToken({ line: line, col: i - lineStart + 1 }));
```

So `1 +` reports `unexpected end of input at 1:4`: the fourth column, where the
next character would have been.

### Module 4's text, unchanged

The scanner's own error is `fail(`unexpected '${ch}'`, pos)` — and formatted,
that is exactly module 4's `error: unexpected '$' at 1:3`. The format has not
changed; it has spread.
""",
    """
```bash
$ printf 'let x = 4;\\nx * y' | node calc.ts
error: undefined variable 'y' at 2:5
$ echo '1 +' | node calc.ts
error: unexpected end of input at 1:4
```

`y` is the fifth character of the second line — not the fifteenth character of
the input.
""",
    pitfalls=[
        "`col: i + 1` — the module 4 formula. Correct on line 1 and wrong on every other line, by the length of everything before it.",
        "`lineStart = i` BEFORE `i = i + 1`. Every column on a new line is then one too big.",
        "Positioning a token at the character AFTER it — computing `pos` after the inner loop. A number's error would point past it.",
        "Treating `\\r` as unexpected. Every program from a Windows editor with more than one line fails on its first line ending.",
    ],
    warmup=[
        _pq("The source is `let x = 4;\\nx * y`. What is the position of `y`?",
            ["2:5 — second line, fifth character of that line",
             "1:15",
             "2:4",
             "1:5"],
            0,
            "The column counts from the start of the line: `i - lineStart + 1`."),
    ],
    exercises=[
        _pex("calc-m16-lines-1", "A new line",
             "Handle a newline: move past it, count a new line, and remember "
             "where the new line starts.",
             _C16_FULL,
             '      i = i + 1;\n      line = line + 1;\n      lineStart = i;',
             _C16_TESTS,
             ["Three variables change.",
              "The new line starts at the character AFTER the newline.",
              "`i = i + 1; line = line + 1; lineStart = i;`"]),
        _pfix("calc-m16-lines-fix1", "Right on line one, wrong below",
              "`let x = 4;\\nx * y` reports `undefined variable 'y' at 2:15`. The "
              "`y` is the fifth character of line 2. Every error on line 1 is "
              "correct.",
              _c16(scan=_C16_SCAN.replace("col: i - lineStart + 1 };\n", "col: i + 1 };\n", 1)),
              _C16_FULL,
              _C16_TESTS,
              ["The line is right. What is the column counting from?",
               "It counts from the start of the whole input, not the start of the line.",
               "`col: i - lineStart + 1`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does `eof` get the column just past the last character?",
            ["That is where the missing thing would have gone — `1 +` needed something at column 4",
             "Because `eof` is a character",
             "Because columns start at 0",
             "It gets column 1"],
            0,
            "An error at the end of the input points at the end of the input."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — errors that carry a place.
# ---------------------------------------------------------------------------

_C16_S3 = _pstep(
    "errors", "Errors that carry a place",
    "`CalcError`, `fail`, and one function that turns any error into text.",
    """
Until now a failure's `error` was a finished string. Now it is data:

```ts
type CalcError = { message: string; pos: Pos };
type Failure = { ok: false; error: CalcError };

function fail(message: string, pos: Pos): Failure {
  return { ok: false, error: { message: message, pos: pos } };
}
```

Every place that built an error string now calls `fail` with a message and a
position:

```ts
return fail(`unexpected ${describe(t)}`, t.pos);            // parser
return fail(`undefined variable '${e.name}'`, e.pos);       // evaluator
return fail("division by zero", pos);                       // arithmetic
```

The messages lose their `error: ` prefix — that is formatting, and formatting
now happens in exactly one place:

```ts
function formatError(err: CalcError): string {
  return `error: ${err.message} at ${err.pos.line}:${err.pos.col}`;
}
```

`run` calls it for each stage's failure.

### Why data, not text

Because `Failure` was named once in module 6, changing what an error IS meant
changing one type — and then the compiler listed every `{ ok: false, error: "…" }`
that no longer fit. That is the second retrofit in this module that the compiler
drove.

And because the position is now a field rather than digits inside a sentence,
module 17 can *use* it: find line 2, print it, and put a caret under column 5.
You cannot do that with a string, short of parsing your own error messages.

### The contract, extended

Module 4 fixed the format `error: <what> at <line>:<col>`. Scan errors always had
it. Every other error now gains the ` at L:C` — the extension module 6 promised.
""",
    """
```bash
$ echo '1 + )' | node calc.ts
error: unexpected ')' at 1:5
$ echo '(1 + 2' | node calc.ts
error: expected ')' but found end of input at 1:7
$ echo 'let x 4' | node calc.ts
error: expected '=' but found '4' at 1:7
```

The brief's example, at last: `unexpected ')' at 1:5`.
""",
    pitfalls=[
        "Formatting inside `fail`: `error: … at …` as the message. Then module 17 has a string to parse instead of a position to use.",
        "Formatting in several places — `run` for scan errors, the parser for its own. Two copies of a format drift.",
        "Returning `parsed.error.message` from `run`: the message with no `error:` and no position.",
    ],
    warmup=[
        _pq("Why does a failure carry a `CalcError` object rather than a formatted string?",
            ["Later code (module 17's caret) needs the position as data, and formatting belongs in one place",
             "Objects are faster than strings",
             "Because TypeScript requires it",
             "No reason"],
            0,
            "Keep data as data until the edge."),
    ],
    exercises=[
        _pex("calc-m16-errors-1", "The only format",
             "Finish `formatError`: `error: <message> at <line>:<col>`.",
             _C16_FULL,
             "  return `error: ${err.message} at ${err.pos.line}:${err.pos.col}`;",
             _C16_TESTS,
             ["A template literal with three holes.",
              "The position is nested: `err.pos.line`.",
              "`return `error: ${err.message} at ${err.pos.line}:${err.pos.col}`;`"]),
        _pfix("calc-m16-errors-fix1", "Half the errors are unformatted",
              "Scan errors print correctly. Parse errors print just their message — "
              "`unexpected ')'`, with no `error:` and no position.",
              _c16(run=_C16_RUN_FN.replace("    return formatError(parsed.error);",
                                           "    return parsed.error.message;")),
              _C16_FULL,
              _C16_TESTS,
              ["Which stage's failure is printed differently?",
               "Every error goes through the same function.",
               "`return formatError(parsed.error);`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("How many places in `calc.ts` produce the text `error: … at L:C`?",
            ["One — `formatError`",
             "One per stage",
             "One per kind of error",
             "None; the messages include it"],
            0,
            "One format, one function."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — nodes remember too.
# ---------------------------------------------------------------------------

_C16_S4 = _pstep(
    "nodes", "Where an evaluation error points",
    "Every node carries the position of the token that made it — and the operator, not the operand, is where arithmetic fails.",
    """
Evaluation errors happen at nodes, so nodes carry positions. Which position is a
decision, and it is made once here and relied on by module 17's caret:

| Error | Points at | Example |
|---|---|---|
| division by zero, too large, cannot apply/compare | the **operator** | `1 + 2 / 0` → `1:7`, the `/` |
| undefined variable | the name | `x * y` → the `y` |
| a literal too large | the literal | `999…9` → `1:1` |
| cannot apply `-` | the `-` | `  -true` → `1:3` |
| condition not a boolean | the `if` | `if 1 then …` → `1:1` |

So the parser passes the right token's position into each factory:

```ts
left = binary(t.op, left, right.expr, t.pos);      // t is the operator token
return { ok: true, expr: neg(operand.expr, t.pos) };   // t is the '-'
```

and the evaluator passes the node's position to `fail`:

```ts
return apply(e.op, left.value, right.value, e.pos);
```

### Why the operator

In `total / count`, the problem when `count` is zero is not `total`, and it is
not really `count` either — `count` being zero is fine on its own. The problem is
the *division*. Pointing at the `/` says "this operation could not be done",
which is exactly the message.

### The unreachable token

`peek`'s fallback — the branch that cannot run — now has to invent a position
for an `eof` that cannot exist:

```ts
return eofToken({ line: 0, col: 0 });
```

Line 0 does not exist, which is honest: this token never came from the source.
It is still a small lie in code that promises it cannot run, and module 17 has
the right tool for "this cannot happen" — one that does not need to invent
anything.
""",
    """
```bash
$ echo '1 + 2 / 0' | node calc.ts
error: division by zero at 1:7
$ printf 'let a = 1;\\nlet b = 0;\\na / b' | node calc.ts
error: division by zero at 3:3
$ echo 'if 1 then 2 else 3' | node calc.ts
error: if condition must be a boolean at 1:1
```
""",
    pitfalls=[
        "The node's position taken from its left operand. `1 + 2 / 0` then blames the `2`, at column 5.",
        "Positions only on tokens. Evaluation has no tokens — only nodes — so every runtime error would have no place.",
        "`binary(…, left.pos)` where `left` is an `Expr` — compiles, and points at the wrong thing for every nested operation.",
    ],
    warmup=[
        _pq("In `1 + 2 / 0`, where does the division error point?",
            ["1:7 — the `/` operator",
             "1:5 — the `2`",
             "1:9 — the `0`",
             "1:1 — the start"],
            0,
            "The operation that could not be done."),
    ],
    exercises=[
        _pex("calc-m16-nodes-1", "The name that is missing",
             "In `evaluate`'s `var` case, fail at the variable's own position.",
             _C16_FULL,
             "        return fail(`undefined variable '${e.name}'`, e.pos);",
             _C16_TESTS,
             ["The node knows where its name was.",
              "`fail(message, position)`.",
              "`return fail(`undefined variable '${e.name}'`, e.pos);`"]),
        _pfix("calc-m16-nodes-fix1", "Blaming the wrong number",
              "`1 + 2 / 0` says `division by zero at 1:5` — the `2`. The division "
              "is at column 7.",
              _c16(product=_C16_PRODUCT.replace("binary(t.op, left, right.expr, t.pos)",
                                                "binary(t.op, left, right.expr, left.pos)")),
              _C16_FULL,
              _C16_TESTS,
              ["Which position does a `*` or `/` node record?",
               "It records its left operand's — so the error points at the `2`.",
               "The operator token is `t`: `binary(t.op, left, right.expr, t.pos)`."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does an arithmetic error point at the operator rather than an operand?",
            ["The operation is what could not be done; either operand is fine on its own",
             "Because operators come first",
             "Because operands have no position",
             "It points at the right operand"],
            0,
            "Decided here; module 17's caret depends on it."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C16_FINAL = _pch(
    "calc-m16-build", "Module 16 build — every error has a place", "Hard",
    "Write the scanner with positions, from `DIGITS` to the end of `scan`:\n\n"
    "* `line` and `lineStart` alongside `i`; a `pos` for every character\n"
    "* `\\n` starts a new line; a space or `\\r` is skipped\n"
    "* every factory call passes `pos` — numbers and words the position they "
    "started at\n"
    "* `eof` positioned just past the last character\n"
    "* an unknown character is `fail(`unexpected '<ch>'`, pos)`\n\n"
    "Several tests span more than one line; one uses `\\r\\n`.",
    _C16_FULL,
    _C16_SCAN.rstrip("\n"),
    _C16_TESTS,
    ["Module 15's scanner, plus two variables and a `pos` at the top of the loop.",
     "`const pos: Pos = { line: line, col: i - lineStart + 1 };`",
     "On `\\n`: advance, count the line, and set `lineStart` to the new `i`.",
     "The `eof` position is computed the same way, after the loop."],
)


_CALC_MODULES.append(_pmod(
    key="calc-positions", number=16, phase="usable",
    title="Line and column on every token",
    what="carry the position from the scanner, or you can never report it",
    goal="Attach a position to every token and every node, and put it in every error.",
    why=_C16_WHY,
    est_minutes=50,
    builds_on=["calc-token", "calc-scan-errors", "calc-cursor", "calc-if"],
    concepts=["source positions", "retrofitting through factories",
              "multi-line input", "errors as data", "one formatter",
              "choosing what an error points at"],
    deliverable="Every error names its line and column — `error: unexpected ')' at "
                "1:5`, `error: undefined variable 'y' at 2:5` — and programs can span "
                "several lines.",
    objectives=[
        "Add a position to every token and node, and explain why factories make that a small change",
        "Track line and column in the scanner, including across `\\n` and `\\r\\n`",
        "Position the end of the input, and say why there",
        "Turn errors into data — a message and a position — formatted in one place",
        "Decide what each kind of evaluation error points at, and justify pointing at operators",
    ],
    brief=_C16_BRIEF,
    syntax=_C16_SYNTAX,
    steps=[_C16_S1, _C16_S2, _C16_S3, _C16_S4],
    final_build=_C16_FINAL,
    acceptance=[
        "`echo '1 + )' | node calc.ts` prints `error: unexpected ')' at 1:5`.",
        "`echo '1 $ 2' | node calc.ts` still prints exactly `error: unexpected '$' at 1:3`.",
        "`printf 'let x = 4;\\nx * y' | node calc.ts` prints `error: undefined variable 'y' at 2:5`.",
        "`echo '1 + 2 / 0' | node calc.ts` prints `error: division by zero at 1:7`.",
        "`echo '1 +' | node calc.ts` prints `error: unexpected end of input at 1:4`.",
        "A program saved with Windows line endings runs.",
        "There is exactly one function that formats an error as text.",
    ],
    manual_test="""
Multi-line input is easiest with `printf`, which understands `\\n`:

```bash
echo '1 + )'                              | node calc.ts   # at 1:5
echo '(1 + 2'                             | node calc.ts   # expected ')' … at 1:7
echo '1 + 2 / 0'                          | node calc.ts   # division by zero at 1:7
printf 'let x = 4;\\nx * y'                | node calc.ts   # undefined variable 'y' at 2:5
printf 'let a = 1;\\nlet b = 0;\\na / b'    | node calc.ts   # at 3:3
printf 'let x = 1;\\r\\nx + 1'              | node calc.ts   # 2 — Windows line ending
```

Better still, put a program in a file with your editor, deliberately break it on
line 3, and run `node calc.ts < prog.calc`. Then open the file at the line and
column the error names — the cursor should land on the culprit.

Finally, repeat module 1's argument for yourself: search `calc.ts` for
`kind: "number"`, `kind: "op"` or `kind: "binary"`. Every hit is inside a type or
a factory — no token or node is built anywhere else. That is why this module was
an afternoon and not a week.
""",
    reference="""// calc.ts — module 16
//
// Every token and node carries a Pos { line, col }. The scanner tracks line and
// lineStart; `\\n` starts a new line and `\\r` is whitespace. Errors are DATA —
// CalcError { message, pos } built by fail() — and formatError() is the one
// place they become `error: <message> at <line>:<col>`.
//
// Where errors point: tokens at themselves, eof just past the last character,
// arithmetic and type errors at the OPERATOR, undefined names at the name.
//
// This was a small change because tokens and nodes have only ever been built by
// factories (modules 1 and 5): add a parameter, and the compiler lists every call.
""" + _C16_FULL,
    stretch=[
        "Make a tab advance the column to the next multiple of 4, the way most editors display it. Then decide whether an error should report the column as displayed or as counted.",
        "Give every node a SPAN — start and end position — instead of a point. `1 + 2 / 0` could then highlight `2 / 0` entirely. What position does a binary node's span start at?",
        "Report several parse errors in one run: after an error, skip to the next `;` and carry on parsing. You will need a way to collect errors instead of returning the first.",
        "Store positions as a single index into the source and compute line and column only when formatting. Compare the two designs: which is cheaper to carry, and which is easier to get right?",
    ],
    glossary=[
        _pgloss("source position", "Where something was in the source text — here a line and a column, both from 1."),
        _pgloss("retrofit", "Adding something to code that was not designed for it. Cheap here because of factories."),
        _pgloss("line start", "The index at which the current line began; a column is the distance from it."),
        _pgloss("errors as data", "An error represented as fields (message, position) rather than a finished sentence, so later code can use its parts."),
    ],
    cheatsheet="""
```ts
type Pos = { line: number; col: number };
type NumberToken = { kind: "number"; value: number; pos: Pos };      // every token, every node

// scanner
let line = 1;
let lineStart = 0;
const pos: Pos = { line: line, col: i - lineStart + 1 };             // top of the loop
if (ch === "\\n") { i = i + 1; line = line + 1; lineStart = i; }
tokens.push(eofToken({ line: line, col: i - lineStart + 1 }));       // just past the end

// errors as data, formatted once
type CalcError = { message: string; pos: Pos };
type Failure = { ok: false; error: CalcError };
function fail(message: string, pos: Pos): Failure { … }
function formatError(err: CalcError): string {
  return `error: ${err.message} at ${err.pos.line}:${err.pos.col}`;
}
```

| Input | Output |
|---|---|
| `1 + )` | `error: unexpected ')' at 1:5` |
| `1 +` | `error: unexpected end of input at 1:4` |
| `1 + 2 / 0` | `error: division by zero at 1:7` — the operator |
| `let x = 4;⏎x * y` | `error: undefined variable 'y' at 2:5` |

| Symptom | Cause |
|---|---|
| columns wrong only after line 1 | `col: i + 1` instead of `i - lineStart + 1` |
| error blames an operand | node positioned at `left.pos`, not the operator |
| a parse error with no `at` | `run` returned `.message` instead of `formatError(…)` |
""",
    self_check=[
        "Can you explain why adding `pos` to every token took so few changes?",
        "Can you compute the position of any character in a two-line program by hand?",
        "Can you say where `eof` is positioned and why?",
        "Can you say what each kind of evaluation error points at?",
        "Can you explain why errors became objects rather than strings?",
    ],
    review=[
        _pq("What did module 1's factories buy this module?",
            ["Every token is built in one of thirteen functions, so adding a field changed those and their calls — and the compiler listed the calls",
             "Nothing",
             "Faster scanning",
             "Automatic positions"],
            0,
            "The payoff the roadmap asked to be said out loud."),
        _pq("`let x = 4;\\nx * y` — where is `y`?",
            ["2:5",
             "1:15",
             "2:4",
             "1:5"],
            0,
            "The column counts from the start of its own line."),
        _pq("Where does `error: division by zero` point in `a / b`?",
            ["At the `/`",
             "At `a`",
             "At `b`",
             "At the start of the line"],
            0,
            "The operation that could not be done."),
        _pq("Why is `\\r` treated as whitespace now?",
            ["Windows ends lines with `\\r\\n`, and a multi-line program saved there would otherwise fail on its first line ending",
             "Because it is a space",
             "For speed",
             "It is not"],
            0,
            "Multi-line input brings line-ending conventions with it."),
        _pq("How many functions turn an error into text?",
            ["One — `formatError`",
             "One per stage",
             "Every `fail` call",
             "None"],
            0,
            "Data inside, text at the edge."),
    ],
    milestone="Every token knows where it came from, every error says where it "
              "happened, and a program can span lines. Module 6's debt is paid — "
              "in an afternoon, because of a decision made in module 1. Module 17 "
              "uses the position to point at the problem.",
))
