# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 8 — Parentheses and unary minus.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses modules 6-7's parser pieces.
#
# THE MODULE THAT CLOSES THE GRAMMAR. Brackets are the first thing that makes
# the parser call back to the TOP of its own ladder — `parsePrimary` calls
# `parseExpr` — and that one call is what lets expressions nest without limit.
# `parseExpr` is introduced here as the name for "the top of the grammar", so
# that module 14 changes one line when comparison becomes the new top.
#
# TWO NEW TOKEN KINDS, `lparen`/`rparen` — the kinds module 1 refused to add
# until something needed them. The union grows for the first time since module
# 1, and module 6's `describe` falls through to "end of input" for both. That is
# graded here as a runtime fix (`calc-m8-tokens-fix1`: `1 + )` says "unexpected
# end of input") and it is the concrete case module 10 opens with: nothing told
# you `describe` needed updating.
#
# UNARY MINUS IS A NODE, `neg`, printed `(neg 3)` so it can never be mistaken for
# subtraction. It gets its own rung between product and primary, and it
# recurses on ITSELF (right-associative, correctly: `--3` is `-(-3)`), which is
# the one place in the ladder where step 2 of module 7's rule is deliberately
# inverted — and the module says why.
#
# `expected …` MESSAGES ARRIVE HERE, the ones module 4's table promised: `(1 + 2`
# says `error: expected ')' but found end of input`.
# ---------------------------------------------------------------------------

_C8_TOKENS = """type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type LParenToken = { kind: "lparen" };
type RParenToken = { kind: "rparen" };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | LParenToken | RParenToken | EofToken;

function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

function opToken(op: Op): OpToken {
  return { kind: "op", op: op };
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

_C8_PAREN_BRANCHES = """    } else if (ch === "(") {
      tokens.push(lparenToken());
      i = i + 1;
    } else if (ch === ")") {
      tokens.push(rparenToken());
      i = i + 1;
"""

_C8_SCAN = _C4_SCAN.replace("    } else {\n", _C8_PAREN_BRANCHES + "    } else {\n", 1)

_C8_TREE = """type NumLit = { kind: "num"; value: number };
type Neg = { kind: "neg"; operand: Expr };
type Binary = { kind: "binary"; op: Op; left: Expr; right: Expr };

type Expr = NumLit | Neg | Binary;

function num(value: number): NumLit {
  return { kind: "num", value: value };
}

function neg(operand: Expr): Neg {
  return { kind: "neg", operand: operand };
}

function binary(op: Op, left: Expr, right: Expr): Binary {
  return { kind: "binary", op: op, left: left, right: right };
}

function show(e: Expr): string {
  if (e.kind === "num") {
    return `${e.value}`;
  }
  if (e.kind === "neg") {
    return `(neg ${show(e.operand)})`;
  }
  return `(${e.op} ${show(e.left)} ${show(e.right)})`;
}
"""

_C8_DESCRIBE = """function describe(t: Token): string {
  if (t.kind === "number") {
    return `'${t.value}'`;
  }
  if (t.kind === "op") {
    return `'${t.op}'`;
  }
  if (t.kind === "lparen") {
    return "'('";
  }
  if (t.kind === "rparen") {
    return "')'";
  }
  return "end of input";
}

function unexpectedToken(t: Token): Failure {
  return { ok: false, error: `error: unexpected ${describe(t)}` };
}

function expected(what: string, t: Token): Failure {
  return { ok: false, error: `error: expected ${what} but found ${describe(t)}` };
}
"""

_C8_PRIMARY = """type ParseResult = { ok: true; expr: Expr } | Failure;

function parseExpr(p: Parser): ParseResult {
  return parseSum(p);
}

function parsePrimary(p: Parser): ParseResult {
  const t = advance(p);
  if (t.kind === "number") {
    return { ok: true, expr: num(t.value) };
  }
  if (t.kind === "lparen") {
    const inner = parseExpr(p);
    if (!inner.ok) {
      return inner;
    }
    const close = advance(p);
    if (close.kind !== "rparen") {
      return expected("')'", close);
    }
    return inner;
  }
  return unexpectedToken(t);
}
"""

_C8_UNARY = """function parseUnary(p: Parser): ParseResult {
  const t = peek(p);
  if (t.kind === "op" && t.op === "-") {
    advance(p);
    const operand = parseUnary(p);
    if (!operand.ok) {
      return operand;
    }
    return { ok: true, expr: neg(operand.expr) };
  }
  return parsePrimary(p);
}
"""

_C8_PRODUCT = _C7_PRODUCT.replace("parsePrimary(p)", "parseUnary(p)")
_C8_PARSE = _c7_parse("parseExpr")


def _c8(tokens=_C8_TOKENS, scan=_C8_SCAN, tree=_C8_TREE, describe=_C8_DESCRIBE,
        primary=_C8_PRIMARY, unary=_C8_UNARY, product=_C8_PRODUCT, parse=_C8_PARSE):
    return _stdin(_cjoin(tokens, _C6_RESULTS, _C4_UNEXPECTED, scan, tree, _C6_STATE,
                         describe, primary, unary, product, _C7_SUM, parse, _C6_RUN))


_C8_FULL = _c8()

_C8_INPUTS = ["(1 + 2) * 3", "(1 + 2) * -3", "-(1 + 2)", "--3", "2 * -3", "-2 * 3",
              "2 - -3", "((7))", "1 - (2 - 3)", "8 / (4 / 2)", "1 + 2 * 3",
              "(1 + 2", "(1 2)", "()", "1 + )", ")", "-", "(", "1 $ 2"]
_C8_TESTS = _ctests(8, _C8_INPUTS)
_C8_PAREN_TESTS = _ctests(8, ["(1 + 2) * 3", "((7))", "1 - (2 - 3)", "8 / (4 / 2)",
                              "(1 + 2", "(1 2)", "()", "1 + )", ")", "("])

_C8_WHY = (
    "The parser now knows that `*` binds tighter than `+`, and there is no way to "
    "tell it otherwise. `(1 + 2) * 3` is a scan error — the scanner has never seen "
    "a bracket — and so is the `-` in `2 * -3`, which the parser reads as a "
    "subtraction with nothing on its left. Both are the same missing piece: a way "
    "for a primary to be more than a number. Brackets let a whole expression sit "
    "where a number would go, which means the bottom of the ladder has to call "
    "back to the top — and that one call is what makes the language able to nest "
    "without limit."
)

_C8_BRIEF = """
### The whole module in one line

`(1 + 2) * -3` parses to `(* (+ 1 2) (neg 3))` — brackets send the parser back
to the top of its grammar, and a minus sign in front of something negates it.

### Two new tokens, and a union that grows

```ts
type LParenToken = { kind: "lparen" };
type RParenToken = { kind: "rparen" };
type Token = NumberToken | OpToken | LParenToken | RParenToken | EofToken;
```

These are the kinds module 1 refused to add until something needed them. Adding
them is the first time the `Token` union has grown since it was written — and
step 1 is about what *else* has to change when a union grows, and how you find
out.

### Brackets: the loop that makes the language infinite

A bracketed expression can go anywhere a number can, so it is a **primary**:

```
primary  =  number  |  "(" expr ")"
```

and `expr` is the top of the ladder — the loosest level, `sum`. So
`parsePrimary`, the *last* function in the chain, calls `parseExpr`, the *first*:

```
parseExpr → parseSum → parseProduct → parseUnary → parsePrimary
    ↑                                                    │
    └───────────────────  "("  ─────────────────────────┘
```

That arrow is the most important line in the parser. Without it, the grammar can
describe expressions only as deep as its ladder is tall. With it, `((((1))))` is
fine, and so is any nesting anyone will ever type.

### Unary minus: a new node, a new rung

`-3` is not `0 - 3` with the `0` missing; it is its own operation, **negation**,
with one operand:

```ts
type Neg = { kind: "neg"; operand: Expr };
```

printed as `(neg 3)` so no one confuses it with subtraction. It binds tighter
than `*` — `-2 * 3` is `(-2) * 3` — so it gets a rung of its own, between
product and primary.

### And the parser learns to say `expected`

```
$ echo '(1 + 2' | node calc.ts
error: expected ')' but found end of input
```

Module 4's message table promised this: when the parser knows exactly what
should come next, it says so.
"""

_C8_SYNTAX = [
    _syn(
        "type Token = NumberToken | OpToken | LParenToken | RParenToken | EofToken;",
        "Growing a union: declare the new member types and add them to the list. "
        "Every value of the old union is still a value of the new one.",
        """
type LParenToken = { kind: "lparen" };
type RParenToken = { kind: "rparen" };
""",
        "Growing a union is easy. Finding every function that switches on it is "
        "not — that is step 1's lesson and module 10's whole subject.",
    ),
    _syn(
        "type Neg = { kind: \"neg\"; operand: Expr };",
        "A node with ONE child. Recursive like `Binary`, with a single `Expr` "
        "inside.",
        """
neg(num(3))                        // -3
neg(binary("+", num(1), num(2)))   // -(1 + 2)
""",
        "",
    ),
    _syn(
        "function parseExpr(p: Parser): ParseResult { return parseSum(p); }",
        "A name for the top of the grammar. Anything that means \"a whole "
        "expression, whatever comes\" calls this rather than naming a level.",
        "",
        "It looks like pointless indirection. Module 14 puts a new level below "
        "`parseSum`, and this is the only line that changes.",
    ),
    _syn(
        "return expected(\"')'\", close);",
        "A failure for when the parser knows exactly what it wanted: `error: "
        "expected ')' but found end of input`.",
        """
function expected(what: string, t: Token): Failure {
  return { ok: false, error: `error: expected ${what} but found ${describe(t)}` };
}
""",
        "`what` arrives with its own quotes, so the same function can later say "
        "`expected a name` without them.",
    ),
    _syn(
        "const operand = parseUnary(p);",
        "Recursion on the same rung: the operand of a minus can itself start with "
        "a minus. `--3` is `-(-3)`.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — two new tokens, and what else has to change.
# ---------------------------------------------------------------------------

_C8_S1 = _pstep(
    "tokens", "Two new tokens, and a union that grows",
    "`lparen` and `rparen` in the scanner — and the function that silently needed them too.",
    """
First the scanner. Two new kinds, two factories, two branches:

```ts
type LParenToken = { kind: "lparen" };
type RParenToken = { kind: "rparen" };

type Token = NumberToken | OpToken | LParenToken | RParenToken | EofToken;
```

```ts
} else if (ch === "(") {
  tokens.push(lparenToken());
  i = i + 1;
} else if (ch === ")") {
  tokens.push(rparenToken());
  i = i + 1;
} else {
  return { ok: false, error: unexpected(ch, i) };
}
```

Why not one `paren` kind with a field saying which? Because the parser never
asks "is this a bracket?" — it asks "is this an *opening* bracket?" and, later,
"is this the *closing* bracket I need?". Two different questions, two kinds.
Module 1 grouped the four operators because the parser *does* ask "is this an
operator?" and only then which one.

### What else has to change

Now go and find every function that looks at a token's `kind`. There is one you
might not think of: `describe`, from module 6.

```ts
function describe(t: Token): string {
  if (t.kind === "number") { … }
  if (t.kind === "op") { … }
  return "end of input";          // ← everything else
}
```

Its last line was written when "everything else" meant `eof`. Now it also means
both brackets — so `1 + )` would report `error: unexpected end of input`, about a
program that very clearly has a `)` in it. The compiler did not say a word:
`describe` still returns a string for every token, which is all its type
promises.

So `describe` gets two branches of its own:

```ts
if (t.kind === "lparen") {
  return "'('";
}
if (t.kind === "rparen") {
  return "')'";
}
```

Remember how you found this: by reading. Module 10 is about never having to
again.
""",
    """
```bash
$ echo '1 + )' | node calc.ts
error: unexpected ')'
$ echo ')' | node calc.ts
error: unexpected ')'
```

If either says `end of input`, `describe` is still falling through.
""",
    pitfalls=[
        "Adding the token kinds and forgetting `describe`. Nothing fails to compile; the error messages quietly lie about brackets.",
        "One `paren` kind with an `open: boolean`. Every check becomes two checks, and `{ kind: \"paren\", open: true }` is a clumsier way to say `lparen`.",
        "Pushing the bracket and forgetting `i = i + 1`. The scanner pushes `lparen` forever.",
        "Treating a bracket as an operator with `Op = … | \"(\"`. A bracket does not combine two operands; it would have to be excluded from every operator check.",
    ],
    warmup=[
        _pq("After adding `lparen` and `rparen` to `Token`, which existing function gives a WRONG answer without any compile error?",
            ["`describe` — its fall-through `return` now covers the brackets too, and calls them the end of input",
             "`peek`",
             "`advance`",
             "`scan`"],
            0,
            "A fall-through is a promise about which kinds exist. Growing the union "
            "breaks the promise silently."),
    ],
    exercises=[
        _pfix("calc-m8-tokens-fix1", "A bracket called the end of the input",
              "`1 + )` says `error: unexpected end of input`. So does `)` on its "
              "own. Both programs obviously have a `)` in them — the parser found "
              "it, and the message describes it wrongly.",
              _c8(describe=_C8_DESCRIBE.replace(
                  '  if (t.kind === "lparen") {\n    return "\'(\'";\n  }\n  if (t.kind === "rparen") {\n    return "\')\'";\n  }\n', "")),
              _C8_FULL,
              _C8_TESTS,
              ["Which function turns a token into the words in the message?",
               "Look at its last line. Which token kinds reach it now?",
               "Give each bracket its own branch, before the fall-through.",
               "`if (t.kind === \"rparen\") { return \"')'\"; }` — and the same for `lparen`."],
              difficulty="Easy"),
        _pex("calc-m8-tokens-1", "Scan a closing bracket",
             "Add the scanner branch for `)`: push a closing-bracket token and "
             "move on.",
             _C8_FULL,
             '    } else if (ch === ")") {\n      tokens.push(rparenToken());\n      i = i + 1;\n',
             _C8_PAREN_TESTS,
             ["Same shape as the `(` branch above it.",
              "Every branch moves the cursor itself.",
              "`} else if (ch === \")\") { tokens.push(rparenToken()); i = i + 1;`"]),
    ],
    quiz=[
        _pq("Why are `(` and `)` two token kinds while `+ - * /` are one?",
            ["The parser asks \"is this an operator?\" and then which — but it never asks \"is this some bracket?\", only which one",
             "Brackets are more important",
             "Because there are only two of them",
             "No reason"],
            0,
            "Token kinds follow the questions the parser asks."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — back to the top.
# ---------------------------------------------------------------------------

_C8_S2 = _pstep(
    "brackets", "Back to the top of the grammar",
    "A bracketed expression is a primary — so the bottom of the ladder calls the top.",
    """
Anywhere a number can go, a bracketed expression can go: `(1 + 2) * 3` has one
where the `1` of `1 * 3` would be. So brackets belong in `parsePrimary`:

```
primary  =  number  |  "(" expr ")"
```

```ts
if (t.kind === "lparen") {
  const inner = parseExpr(p);
  if (!inner.ok) {
    return inner;
  }
  const close = advance(p);
  if (close.kind !== "rparen") {
    return expected("')'", close);
  }
  return inner;
}
```

Between the brackets is a **whole expression** — the loosest kind, with `+` in
it — so the call is to the top of the ladder. Give the top a name:

```ts
function parseExpr(p: Parser): ParseResult {
  return parseSum(p);
}
```

and have `parse` start there too. One function now means "an expression,
whatever is in it"; module 14 will change what it calls, and nothing that calls it
will notice.

### Why `(1 + 2) * 3` comes out right

`parseProduct` asks for a primary. The primary is `(`, so it parses a whole
expression — `1 + 2`, built by `parseSum` as usual — and checks for `)`. It hands
back `(+ 1 2)` as if it were a single number. `parseProduct` multiplies it by 3.
The `+` ended up *under* the `*` because it was parsed in a call made *by* the
product level.

### The brackets vanish

`return inner;` — not a `paren` node. Module 5 said the tree would have no node
for brackets, because the shape already says what they said, and here is where
that is made true. `((7))` parses to `7`.

### `expected`, at last

After the inner expression, only `)` will do. When the parser knows exactly what
it wants, it says so:

```ts
function expected(what: string, t: Token): Failure {
  return { ok: false, error: `error: expected ${what} but found ${describe(t)}` };
}
```

`(1 + 2` gives `error: expected ')' but found end of input`, and `(1 2)` gives
`error: expected ')' but found '2'`.
""",
    """
```bash
$ echo '(1 + 2) * 3' | node calc.ts
(* (+ 1 2) 3)
$ echo '((7))' | node calc.ts
7
$ echo '(1 + 2' | node calc.ts
error: expected ')' but found end of input
```

Brackets change the tree and then disappear from it.
""",
    pitfalls=[
        "Calling `parsePrimary` or `parseProduct` for the inside of the brackets. `(1 + 2)` then fails at the `+`, because only the top of the ladder handles it.",
        "Returning a `paren` node. It evaluates to the same thing as its contents — and every later function over `Expr` has to handle a node that means nothing.",
        "Checking for `)` with `peek` and never advancing past it. The `)` is still there for `parseProduct` to trip over.",
        "`unexpectedToken(close)` for a missing `)`. True, but `expected ')'` tells the user what would have fixed it.",
    ],
    warmup=[
        _pq("Why does `parsePrimary` call `parseExpr` rather than `parseProduct` for what is inside `( )`?",
            ["Anything can go inside brackets — including `+`, which only the top of the ladder handles",
             "Because `parseProduct` does not exist yet",
             "Because brackets are low precedence",
             "It makes no difference"],
            0,
            "Inside brackets you are back at the start: any expression at all."),
    ],
    exercises=[
        _pex("calc-m8-brackets-1", "An expression in brackets",
             "In `parsePrimary`, after an opening bracket: parse a whole "
             "expression, then insist on the closing bracket.",
             _C8_FULL,
             '    const inner = parseExpr(p);\n    if (!inner.ok) {\n      return inner;\n    }\n    const close = advance(p);\n    if (close.kind !== "rparen") {\n      return expected("\')\'", close);\n    }\n    return inner;\n',
             _C8_PAREN_TESTS,
             ["What can go between brackets? Call the function for that.",
              "Pass a failure up. Then take the next token: it must be `)`.",
              "If it is not, `expected(\"')'\", close)`. If it is, the inner expression IS the result — no new node.",
              "`const inner = parseExpr(p); … const close = advance(p); if (close.kind !== \"rparen\") { return expected(\"')'\", close); } return inner;`"]),
        _pex("calc-m8-brackets-2", "Say what was wanted",
             "Finish `expected`: a failure reading `error: expected <what> but "
             "found <description of the token>`.",
             _C8_FULL,
             "  return { ok: false, error: `error: expected ${what} but found ${describe(t)}` };",
             _C8_PAREN_TESTS,
             ["Same shape as `unexpectedToken`.",
              "`what` already has its quotes; `describe(t)` supplies the token's.",
              "`return { ok: false, error: `error: expected ${what} but found ${describe(t)}` };`"]),
    ],
    quiz=[
        _pq("What does `((7))` parse to, and why?",
            ["`7` — each bracket pair returns its inner expression unchanged; there is no bracket node",
             "`(paren (paren 7))`",
             "An error",
             "`(7)`"],
            0,
            "Brackets steer the parse and leave no trace in the tree."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — unary minus.
# ---------------------------------------------------------------------------

_C8_S3 = _pstep(
    "unary", "Unary minus",
    "A `neg` node, a rung of its own between product and primary, and `--3`.",
    """
`2 * -3` still fails: `parseProduct` asks for a primary and gets a `-`. A minus
*in front of* something is not subtraction — nothing is on its left — so it is a
different operation, with its own node:

```ts
type Neg = { kind: "neg"; operand: Expr };
type Expr = NumLit | Neg | Binary;

function neg(operand: Expr): Neg {
  return { kind: "neg", operand: operand };
}
```

and `show` prints it as `(neg 3)` — never `(- 3)`, which would read as a
subtraction with a side missing.

### Where it goes on the ladder

`-2 * 3` means `(-2) * 3`: the minus binds tighter than `*`. So it is a new rung,
between product and primary:

```
product  =  unary ( ("*" | "/") unary )*
unary    =  "-" unary  |  primary
```

```ts
function parseUnary(p: Parser): ParseResult {
  const t = peek(p);
  if (t.kind === "op" && t.op === "-") {
    advance(p);
    const operand = parseUnary(p);
    if (!operand.ok) {
      return operand;
    }
    return { ok: true, expr: neg(operand.expr) };
  }
  return parsePrimary(p);
}
```

and `parseProduct` asks `parseUnary` for its operands, where it used to ask
`parsePrimary`.

### Recursing on its own rung — on purpose

Module 7's rule was: the operand comes from the level *above*, never your own,
or chains lean right. `parseUnary` breaks it deliberately. `--3` should be
`-(-3)`: the *inner* minus is applied first, so it is deeper — a right-leaning
chain, which is exactly what recursing on your own rung builds. Prefix operators
are right-associative by nature: the one nearest the operand goes first.

### Why the same `-` token can mean two things

The scanner makes one `op -` token for both. The *parser* tells them apart by
position: a `-` where an operand is expected (the start, after `(`, after
another operator) is negation; a `-` after a complete operand is subtraction.
`parseUnary` only ever sees the first kind, because `parseSum` has already
taken every `-` that follows an operand.
""",
    """
```bash
$ echo '2 * -3' | node calc.ts
(* 2 (neg 3))
$ echo '-2 * 3' | node calc.ts
(* (neg 2) 3)
$ echo '2 - -3' | node calc.ts
(- 2 (neg 3))
$ echo '--3' | node calc.ts
(neg (neg 3))
```

In `2 - -3`, the first `-` is subtraction and the second is negation — same
token, told apart by where it stands.
""",
    pitfalls=[
        "`parseProduct` still calling `parsePrimary`. `-3` parses at the start of a sum (if `parseSum` is fixed) but `2 * -3` fails with `unexpected '-'`.",
        "Parsing the operand with `parsePrimary`. `-(1 + 2)` still works, and `--3` fails — so only a test with two minuses catches it.",
        "Rewriting `-3` as `binary(\"-\", num(0), num(3))`. The value is right; the tree lies about the source, and module 14 will want to reject `-true` with its own message.",
        "Putting the unary rung below `parseSum`. `-2 * 3` then parses as `-(2 * 3)` — the same number here, and a different tree.",
    ],
    warmup=[
        _pq("How does the parser know the second `-` in `2 - -3` is negation?",
            ["It appears where an operand is expected — right after an operator — so `parseUnary` sees it",
             "The scanner gives it a different token kind",
             "Negation is always the last `-`",
             "It does not; `2 - -3` is an error"],
            0,
            "Position decides. One token kind, two meanings."),
    ],
    exercises=[
        _pex("calc-m8-unary-1", "Minus, then anything that could follow a minus",
             "In `parseUnary`, after taking the `-`, parse its operand — which may "
             "itself start with a minus — and wrap it in a `neg` node.",
             _C8_FULL,
             "    const operand = parseUnary(p);\n    if (!operand.ok) {\n      return operand;\n    }\n    return { ok: true, expr: neg(operand.expr) };",
             _C8_TESTS,
             ["`--3` has to work. What must the operand parser accept?",
              "This rung recurses on itself, on purpose.",
              "`const operand = parseUnary(p);`, pass a failure up, then `neg(operand.expr)`."]),
        _pfix("calc-m8-unary-fix1", "Two times minus three",
              "`-3` parses. `-(1 + 2)` parses. `2 * -3` says `error: unexpected "
              "'-'`.",
              _c8(product=_C7_PRODUCT),
              _C8_FULL,
              _C8_TESTS,
              ["Where does a minus at the very start get handled? Where does the operand of a `*` come from?",
               "The product level asks the wrong rung for its operands.",
               "`parseProduct` should call `parseUnary` in both places it calls `parsePrimary`."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does `parseUnary` recurse on itself, when module 7 said that makes chains lean right?",
            ["Prefix minus IS right-associative — in `--3` the inner minus applies first, so it belongs deepest",
             "It is a bug that happens to work",
             "Because unary minus has no precedence",
             "It does not recurse"],
            0,
            "The rule was \"loop for left-associative\". Prefix operators are the "
            "other kind."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the grammar is complete.
# ---------------------------------------------------------------------------

_C8_S4 = _pstep(
    "complete", "The grammar is complete",
    "Five rungs, one loop back to the top, and every arithmetic expression anyone can type.",
    """
Here is the whole language, as grammar and as code — the same thing written
twice:

```
expr     =  sum
sum      =  product ( ("+" | "-") product )*
product  =  unary   ( ("*" | "/") unary )*
unary    =  "-" unary  |  primary
primary  =  number  |  "(" expr ")"
```

```
parse → parseExpr → parseSum → parseProduct → parseUnary → parsePrimary
            ↑                                                   │
            └──────────────────────  "("  ─────────────────────┘
```

Every arithmetic expression over `+ - * /`, brackets and negation parses to the
tree it means, and nothing else parses. That is what phase 2 promised: *a tree
that already knows `1 + 2 * 3` is an addition whose right-hand side is a
multiplication.*

### The failures, all of them

| Input | Message | From |
|---|---|---|
| `1 +` | `error: unexpected end of input` | a primary that got `eof` |
| `1 + )` | `error: unexpected ')'` | a primary that got `)` |
| `()` | `error: unexpected ')'` | the primary inside the brackets |
| `(1 + 2` | `error: expected ')' but found end of input` | the closing check |
| `(1 2)` | `error: expected ')' but found '2'` | the closing check |
| `1 2` | `error: unexpected '2'` | the end check in `parse` |

Three places can fail: a primary that cannot start, a bracket that is not closed,
and leftovers at the end. Everything else declines and hands over.

### What phase 3 inherits

A tree that is always right, or a message. Module 9's evaluator will be
astonishingly short, and the reason is everything in the table above: it never
has to wonder whether the tree it was given makes sense.
""",
    """
```bash
$ echo '(1 + 2) * -3' | node calc.ts
(* (+ 1 2) (neg 3))
$ echo '1 - (2 - 3)' | node calc.ts
(- 1 (- 2 3))
$ echo '()' | node calc.ts
error: unexpected ')'
```

`1 - (2 - 3)` leans right — because the brackets said so, not because the parser
got it wrong.
""",
    pitfalls=[
        "A separate check for empty brackets `()`. The primary inside already fails with `unexpected ')'`, which is the right message.",
        "Checking the bracket depth with a counter. The call stack already is the counter: each `(` is one call to `parseExpr`, and each return needs its `)`.",
        "Letting `parseSum` stop at `)` with an error. It must decline it silently — the primary that opened the bracket is waiting for it.",
    ],
    warmup=[
        _pq("How does the parser keep track of how many brackets are open?",
            ["It does not need to — each `(` is a nested call, and each call checks for its own `)` before returning",
             "A counter in `Parser`",
             "The scanner counts them",
             "It checks at the end that the counts match"],
            0,
            "The call stack remembers. That is what recursion buys."),
    ],
    exercises=[
        _pch("calc-m8-complete-primary", "The bottom rung", "Medium",
             "Write `parsePrimary` from nothing: a number becomes a number node; "
             "an opening bracket means a whole expression and then a closing "
             "bracket; anything else is unexpected.",
             _C8_FULL,
             "function parsePrimary" + _C8_PRIMARY.split("\n\nfunction parsePrimary")[1].rstrip("\n"),
             _C8_TESTS,
             ["Take a token with `advance`.",
              "Number → `{ ok: true, expr: num(t.value) }`.",
              "`lparen` → `parseExpr`, pass failures up, then `advance` and check for `rparen` with `expected`.",
              "Anything else → `unexpectedToken(t)`."]),
    ],
    quiz=[
        _pq("Which single call makes the grammar able to describe expressions of any depth?",
            ["`parsePrimary` calling `parseExpr` for the inside of brackets",
             "`parseSum` calling `parseProduct`",
             "`parse` calling `parseExpr`",
             "`advance`"],
            0,
            "The bottom of the ladder reaching back to the top. Without it, depth "
            "is limited to the number of rungs."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C8_FINAL = _pch(
    "calc-m8-build", "Module 8 build — the complete grammar", "Hard",
    "Write the whole parser below `show`, from `describe` to `parse`:\n\n"
    "* `describe`, `unexpectedToken` and `expected` — brackets described as "
    "`'('` and `')'`\n"
    "* `ParseResult`, `parseExpr` and `parsePrimary` — numbers and bracketed "
    "expressions\n"
    "* `parseUnary` — a minus in front of any unary\n"
    "* `parseProduct` and `parseSum` — module 7's levels, the product level now "
    "asking `parseUnary` for operands\n"
    "* `parse` — an expression, then `eof`\n\n"
    "The scanner (with brackets), the tree (with `neg`) and the cursor are given.",
    _C8_FULL,
    _cjoin(_C8_DESCRIBE, _C8_PRIMARY, _C8_UNARY, _C8_PRODUCT, _C7_SUM, _C8_PARSE).rstrip("\n"),
    _C8_TESTS,
    ["Work bottom-up: `describe` and the two failure builders first.",
     "`parsePrimary` calls `parseExpr` for brackets; `parseExpr` just calls `parseSum`.",
     "`parseUnary` recurses on itself; `parseProduct` loops and asks `parseUnary`.",
     "Test `1 + )` — if it says `end of input`, `describe` is missing the brackets."],
)


_CALC_MODULES.append(_pmod(
    key="calc-parens", number=8, phase="parse",
    title="Parentheses and unary minus",
    what="recursion back to the top of the grammar, which closes the loop",
    goal="Parse `(1 + 2) * -3`, and every other arithmetic expression anyone can type.",
    why=_C8_WHY,
    est_minutes=45,
    builds_on=["calc-cursor", "calc-precedence"],
    concepts=["growing a union", "fall-through hazards", "mutual recursion",
              "grouping without a node", "prefix operators", "right associativity",
              "expected-token errors"],
    deliverable="`echo '(1 + 2) * -3' | node calc.ts` prints `(* (+ 1 2) (neg 3))`, "
                "and `(1 + 2` says `error: expected ')' but found end of input` — "
                "the grammar is complete.",
    objectives=[
        "Add two token kinds, and find the function that silently needed updating",
        "Parse a bracketed expression as a primary that calls back to the top of the grammar",
        "Explain why brackets leave no node in the tree",
        "Add a unary rung between product and primary, and say why it recurses on itself",
        "Tell subtraction from negation by position alone",
        "Write `expected …` messages for when the parser knows what it wanted",
    ],
    brief=_C8_BRIEF,
    syntax=_C8_SYNTAX,
    steps=[_C8_S1, _C8_S2, _C8_S3, _C8_S4],
    final_build=_C8_FINAL,
    acceptance=[
        "`echo '(1 + 2) * 3' | node calc.ts` prints `(* (+ 1 2) 3)`.",
        "`echo '(1 + 2) * -3' | node calc.ts` prints `(* (+ 1 2) (neg 3))`.",
        "`echo '--3' | node calc.ts` prints `(neg (neg 3))`, and `2 - -3` prints `(- 2 (neg 3))`.",
        "`echo '((7))' | node calc.ts` prints `7` — no node for brackets.",
        "`echo '(1 + 2' | node calc.ts` prints `error: expected ')' but found end of input`.",
        "`echo '1 + )' | node calc.ts` prints `error: unexpected ')'` — not `end of input`.",
    ],
    manual_test="""
```bash
echo '(1 + 2) * 3'     | node calc.ts     # (* (+ 1 2) 3)
echo '(1 + 2) * -3'    | node calc.ts     # (* (+ 1 2) (neg 3))
echo '-(1 + 2)'        | node calc.ts     # (neg (+ 1 2))
echo '2 - -3'          | node calc.ts     # (- 2 (neg 3))
echo '((((7))))'       | node calc.ts     # 7
echo '(1 + 2'          | node calc.ts     # error: expected ')' but found end of input
echo '(1 2)'           | node calc.ts     # error: expected ')' but found '2'
echo '1 + )'           | node calc.ts     # error: unexpected ')'
```

Now the experiment that sets up module 10. Delete the two bracket branches from
`describe` and run `npx tsc --noEmit --strict calc.ts`. No errors. Run
`echo '1 + )' | node calc.ts`: `error: unexpected end of input`. The compiler had
every piece of information it needed to warn you, and did not. Put the branches
back — and remember that it was reading, not the compiler, that found this.
""",
    reference="""// calc.ts — module 8
//
// The complete grammar of arithmetic:
//
//   expr     = sum
//   sum      = product ( ("+" | "-") product )*
//   product  = unary   ( ("*" | "/") unary )*
//   unary    = "-" unary | primary
//   primary  = number | "(" expr ")"
//
// parsePrimary calling parseExpr for brackets is the loop that lets expressions
// nest without limit. Brackets leave no node: the tree's shape says what they said.
""" + _C8_FULL,
    stretch=[
        "Add unary `+`, so `+3` parses. Decide whether it deserves a node or should vanish like brackets do — and what `show` would print either way.",
        "Report unbalanced brackets at the point they were opened: `(1 + (2 * 3` could say which `(` was never closed. What would the parser need to remember?",
        "Write `unparse(e)`: print a tree as ordinary arithmetic with only the brackets that are needed. `(* (+ 1 2) 3)` → `(1 + 2) * 3`, but `(+ 1 (* 2 3))` → `1 + 2 * 3`. You will need each operator's precedence as a number.",
        "Give `show` a third form for `neg` applied to a number: print `-3` instead of `(neg 3)`. Then find the input where that makes two different trees print the same text.",
    ],
    glossary=[
        _pgloss("primary", "The smallest self-contained expression: a number, or a whole expression in brackets."),
        _pgloss("mutual recursion", "Functions that call each other in a cycle — `parseExpr` → … → `parsePrimary` → `parseExpr`."),
        _pgloss("unary operator", "An operator with one operand, like negation in `-3`."),
        _pgloss("prefix operator", "A unary operator written before its operand. Right-associative: `--3` is `-(-3)`."),
        _pgloss("fall-through", "A final `return` that handles \"everything else\". Safe until the union it covers grows."),
    ],
    cheatsheet="""
```
expr     =  sum
sum      =  product ( ("+" | "-") product )*
product  =  unary   ( ("*" | "/") unary )*
unary    =  "-" unary  |  primary
primary  =  number  |  "(" expr ")"
```

```ts
if (t.kind === "lparen") {                   // in parsePrimary
  const inner = parseExpr(p);                // back to the top
  if (!inner.ok) { return inner; }
  const close = advance(p);
  if (close.kind !== "rparen") { return expected("')'", close); }
  return inner;                              // no bracket node
}

function parseUnary(p: Parser): ParseResult {
  const t = peek(p);
  if (t.kind === "op" && t.op === "-") {
    advance(p);
    const operand = parseUnary(p);           // itself: --3 is -(-3)
    if (!operand.ok) { return operand; }
    return { ok: true, expr: neg(operand.expr) };
  }
  return parsePrimary(p);
}
```

| Symptom | Cause |
|---|---|
| `1 + )` says `end of input` | `describe` has no bracket branches |
| `2 * -3` → `unexpected '-'` | `parseProduct` still asks `parsePrimary` |
| `--3` fails | the operand of `-` parsed with `parsePrimary` |
| `(1 + 2)` → `expected ')' but found '+'` | brackets parse `parseProduct`, not `parseExpr` |
""",
    self_check=[
        "Can you write the five grammar rules, and point at the one that makes nesting unlimited?",
        "Can you say which existing function broke silently when the token union grew, and why the compiler said nothing?",
        "Can you explain why `((7))` parses to `7`?",
        "Can you tell negation from subtraction in `2 - -3`, and say which function handles each?",
        "Can you explain why `parseUnary` may recurse on itself when `parseProduct` must not?",
    ],
    review=[
        _pq("Why does `parsePrimary` call `parseExpr` for bracketed expressions?",
            ["A bracket can contain any expression, and only the top of the ladder parses all of them",
             "To save a function call",
             "Because brackets have the lowest precedence",
             "It calls `parseSum` directly"],
            0,
            "And naming the top `parseExpr` means module 14 changes one line."),
        _pq("After adding `rparen`, `describe` still compiles but calls `)` the end of input. Why no compile error?",
            ["Its fall-through `return` covers every remaining kind, so it still returns a string for every token — which is all the type promises",
             "Because `describe` is never called",
             "Because the compiler does not check `if` statements",
             "There is a compile error"],
            0,
            "Module 10's `never` turns this silence into an error."),
        _pq("What tree does `-2 * 3` produce?",
            ["`(* (neg 2) 3)` — unary minus binds tighter than `*`",
             "`(neg (* 2 3))`",
             "`(- 2 3)`",
             "An error"],
            0,
            "The unary rung sits above product, so negation is applied first."),
        _pq("Why is `-3` a `neg` node rather than `0 - 3`?",
            ["It is a different operation with one operand; rewriting it makes the tree lie about the source",
             "Because `0 - 3` is not -3",
             "Trees cannot hold zero",
             "No reason; either is fine"],
            0,
            "Later modules give negation its own error — `cannot apply '-' to a "
            "boolean` — and need to know it was negation."),
        _pq("What does `(1 2)` report?",
            ["`error: expected ')' but found '2'`",
             "`error: unexpected '2'`",
             "`error: unexpected end of input`",
             "`(1 2)`"],
            0,
            "Inside the brackets, after an expression, only `)` will do — and the "
            "parser says so."),
    ],
    milestone="Phase 2 is done. Any arithmetic expression becomes the tree it "
              "means: precedence, associativity, brackets and negation, with a "
              "message naming the token for everything else. Module 9 walks the tree "
              "and gets a number out.",
))
