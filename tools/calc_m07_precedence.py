# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 7 — Precedence, and why `1 + 2 * 3` is 7.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses module 6's parser pieces.
#
# THE CENTREPIECE OF PHASE 2. Recursive descent with ONE FUNCTION PER
# PRECEDENCE LEVEL: `parseSum` handles `+ -` and calls `parseProduct` for its
# operands; `parseProduct` handles `* /` and calls `parsePrimary`. That is the
# "two functions calling each other" of the roadmap, and it is chosen over
# precedence climbing because the grammar can be read straight off the code —
# and because module 14 then adds comparison as one more level, one more
# function, with nothing else touched.
#
# MODULE 1'S GROUPED `op` KIND PAYS HERE: "is this an operator of my level?" is
# `t.kind === "op" && (t.op === "+" || t.op === "-")` — one kind test and a look
# at the symbol — rather than four token kinds tested in two functions.
#
# LEFT ASSOCIATIVITY COMES FROM THE LOOP, and the module's graded fix is the
# classic mistake: recursing into your own level for the right operand, which
# builds `(/ 8 (/ 4 2))` for `8 / 4 / 2`. Module 5 taught why the tree must lean
# left; this is where the code that makes it lean left is written.
#
# No new syntax: a `while` whose condition narrows the token, and `let` rebound
# in a loop. The module is an idea.
# ---------------------------------------------------------------------------

_C7_PRODUCT = """function parseProduct(p: Parser): ParseResult {
  const first = parsePrimary(p);
  if (!first.ok) {
    return first;
  }
  let left = first.expr;
  let t = peek(p);
  while (t.kind === "op" && (t.op === "*" || t.op === "/")) {
    advance(p);
    const right = parsePrimary(p);
    if (!right.ok) {
      return right;
    }
    left = binary(t.op, left, right.expr);
    t = peek(p);
  }
  return { ok: true, expr: left };
}
"""

_C7_SUM = """function parseSum(p: Parser): ParseResult {
  const first = parseProduct(p);
  if (!first.ok) {
    return first;
  }
  let left = first.expr;
  let t = peek(p);
  while (t.kind === "op" && (t.op === "+" || t.op === "-")) {
    advance(p);
    const right = parseProduct(p);
    if (!right.ok) {
      return right;
    }
    left = binary(t.op, left, right.expr);
    t = peek(p);
  }
  return { ok: true, expr: left };
}
"""


def _c7_parse(entry):
    return _C6_PARSE.replace("parsePrimary(p);", f"{entry}(p);", 1)


_C7_PARSE = _c7_parse("parseSum")


def _c7(product=_C7_PRODUCT, sum_=_C7_SUM, parse=_C7_PARSE):
    return _stdin(_cjoin(_C_TOKENS, _C6_RESULTS, _C4_UNEXPECTED, _C4_SCAN, _C6_TREE,
                         _C6_STATE, _C6_DESCRIBE, _C6_PRIMARY, product, sum_, parse, _C6_RUN))


_C7_FULL = _c7()

_C7_INPUTS = ["1 + 2 * 3", "1 * 2 + 3", "10 - 4 - 3", "100 / 10 / 2", "2 * 3 + 4 * 5",
              "1 - 2 + 3", "8 / 4 * 2", "7", "1 +", "* 2", "1 + * 2", "1 2", "",
              "1 + 2 $"]
_C7_TESTS = _ctests(7, _C7_INPUTS)

# Step 1: a grammar of products only — `parse` calls `parseProduct`.
_C7_S1_FULL = _c7(sum_="", parse=_c7_parse("parseProduct"))
_C7_S1_TESTS = _ctests(7, ["2 * 3", "2 * 3 * 4", "8 / 2", "8 / 4 / 2", "6 / 3 * 2", "5", "2 *"]) \
    + _ctests(6, ["1 + 2"])

_C7_WHY = (
    "The parser can read one number. The language needs `1 + 2 * 3` — and it "
    "needs it to mean 7, not 9. That is a decision about which tree five tokens "
    "become, and the tokens arrive in reading order, with the `+` first. So the "
    "parser has to know, before it builds anything, that a `*` further along "
    "binds tighter than the `+` it is looking at. The whole trick is one function "
    "per level of precedence, each calling the next one down. It is the idea every "
    "hand-written parser in the world is built on, and it fits in forty lines."
)

_C7_BRIEF = """
### The whole module in one line

`1 + 2 * 3` parses to `(+ 1 (* 2 3))` — two functions, one per precedence level,
the lower one calling the higher one for its operands.

### The problem, precisely

Reading left to right, the parser meets `1`, then `+`. It cannot build
`(+ 1 2)` yet, because it does not know whether the `2` belongs to the `+` or to
something tighter coming up. It has to parse "the whole right-hand side of the
`+`" — and a right-hand side of a `+` is anything built from `*` and `/`.

### The grammar

Written as rules, where `( … )*` means "zero or more times":

```
sum      =  product ( ("+" | "-") product )*
product  =  primary ( ("*" | "/") primary )*
primary  =  number
```

Read the first line aloud: *a sum is a product, followed by any number of
plus-or-minus-product*. The operands of `+` are **products**, never bare
numbers — so `2 * 3` is swallowed whole as the right side of the `+`. That one
fact is precedence.

### The code is the grammar

Each rule becomes a function with the same name and the same shape:

```ts
function parseSum(p: Parser): ParseResult {        // sum = product (("+"|"-") product)*
  const first = parseProduct(p);
  …
  while (t.kind === "op" && (t.op === "+" || t.op === "-")) {
    advance(p);
    const right = parseProduct(p);
    …
    left = binary(t.op, left, right.expr);
  }
}
```

`parseProduct` is the same function one level up, with `*` and `/`, calling
`parsePrimary`. Two functions; one calls the other; the tree comes out right.

### Where module 1 pays again

"Is this one of my operators?" is `t.kind === "op"` and then a look at `t.op`.
Module 1 made every operator one token kind carrying a symbol precisely so this
test would be one kind check, not four.

### And associativity

The `while` loop builds `left = binary(op, left, right)` over and over, so each
new operation takes everything so far as its *left* side. `10 - 4 - 3` becomes
`(- (- 10 4) 3)` — the left-leaning tree module 5 said it must be.
"""

_C7_SYNTAX = [
    _syn(
        "while (t.kind === \"op\" && (t.op === \"+\" || t.op === \"-\")) { … }",
        "Keep going while the next token is an operator of this level. The "
        "condition narrows `t`: inside the loop it is an `OpToken` whose `op` is "
        "`+` or `-`.",
        """
let t = peek(p);
while (t.kind === "op" && (t.op === "+" || t.op === "-")) {
  advance(p);
  // … t.op is "+" | "-" here
  t = peek(p);
}
""",
        "The inner brackets matter: without them, `&&` binds tighter than `||` and "
        "the condition reads `(kind is op and op is +) or op is -` — which does not "
        "compile, because a token that is not an operator has no `op`.",
    ),
    _syn(
        "let left = first.expr; … left = binary(t.op, left, right.expr);",
        "A variable that is rebound each time round the loop, growing the tree "
        "leftwards: the old tree becomes the left side of the new one.",
        """
// 10 - 4 - 3
left = 10
left = (- 10 4)
left = (- (- 10 4) 3)
""",
        "`let`, not `const`, because it changes. Its type is `Expr` throughout — "
        "a number to begin with, a `Binary` after the first operator.",
    ),
    _syn(
        "function parseSum(p: Parser): ParseResult { … parseProduct(p) … }",
        "One function per precedence level. Each parses its own operators and "
        "asks the level above for its operands.",
        "",
        "The *lower* precedence level is the *outer* function. `+` is at the top "
        "of the tree, so the function that builds `+` nodes runs first and calls "
        "down.",
    ),
    _syn(
        "if (!right.ok) { return right; }",
        "Module 6's pass-it-up line, now inside a loop — a failure halfway through "
        "`1 + 2 * ` ends the whole parse.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — one level: products.
# ---------------------------------------------------------------------------

_C7_S1 = _pstep(
    "product", "One level: products",
    "`parseProduct`: a primary, then any number of `* primary` or `/ primary` — in a loop.",
    """
Start with a language that only multiplies and divides. Its grammar is one rule:

```
product  =  primary ( ("*" | "/") primary )*
```

A product is a primary, then any number of times: a `*` or `/`, and another
primary. The `( … )*` is a loop, and the code says so:

```ts
function parseProduct(p: Parser): ParseResult {
  const first = parsePrimary(p);
  if (!first.ok) {
    return first;
  }
  let left = first.expr;
  let t = peek(p);
  while (t.kind === "op" && (t.op === "*" || t.op === "/")) {
    advance(p);
    const right = parsePrimary(p);
    if (!right.ok) {
      return right;
    }
    left = binary(t.op, left, right.expr);
    t = peek(p);
  }
  return { ok: true, expr: left };
}
```

Walk it for `2 * 3 * 4`:

| Step | Token peeked | `left` afterwards |
|---|---|---|
| first primary | — | `2` |
| loop 1 | `*` | `(* 2 3)` |
| loop 2 | `*` | `(* (* 2 3) 4)` |
| exit | `eof` | — |

Peek to decide whether to go round again; advance to take the operator once you
have decided. When the next token is anything else — `eof`, a `+`, a number — the
loop stops and the product is done. Deciding what that token *means* is somebody
else's job: `parse`'s end check, or, in a moment, `parseSum`.

### The narrowing does real work

Inside the loop, `t.op` is known to be `"*" | "/"`. That is why
`binary(t.op, …)` compiles — `binary` wants an `Op`, and the compiler has proved
this one is.
""",
    """
```bash
$ echo '2 * 3 * 4' | node calc.ts
(* (* 2 3) 4)
$ echo '8 / 4 / 2' | node calc.ts
(/ (/ 8 4) 2)
$ echo '1 + 2' | node calc.ts
error: unexpected '+'
```

With `parse` calling `parseProduct`, products parse and lean left. `+` is still
unexpected — no level handles it yet.
""",
    pitfalls=[
        "Advancing before deciding: `advance`, then checking whether it was `*`. If it was not, a token has been eaten that belonged to someone else.",
        "Forgetting `t = peek(p)` at the bottom of the loop. `t` still holds the old `*`, so the loop runs forever asking for more primaries.",
        "Writing `t.kind === \"op\" && t.op === \"*\" || t.op === \"/\"` without the inner brackets. It does not compile — and the reason it does not is worth reading.",
        "Returning `first` at the end instead of the tree built in the loop. `2 * 3` then parses as `2`, and the end check complains about the `*`.",
    ],
    warmup=[
        _pq("In `parseProduct`, the next token is `+`. What happens?",
            ["The loop stops and the product built so far is returned — `+` is not this level's operator",
             "It is an error: `unexpected '+'`",
             "It advances past the `+`",
             "It calls `parseSum`"],
            0,
            "A level stops at anything it does not handle and lets its caller "
            "decide. That is what makes the levels stack."),
    ],
    exercises=[
        _pex("calc-m7-product-1", "Round again?",
             "Write the loop condition: keep going while the next token is a `*` "
             "or a `/`.",
             _C7_S1_FULL,
             'while (t.kind === "op" && (t.op === "*" || t.op === "/")) {',
             _C7_S1_TESTS,
             ["First check it is an operator at all — only then does `t.op` exist.",
              "Then check which operator, with the two choices bracketed together.",
              "`while (t.kind === \"op\" && (t.op === \"*\" || t.op === \"/\")) {`"]),
        _pex("calc-m7-product-2", "Grow the tree leftwards",
             "Inside the loop, once the right operand is parsed, make a new "
             "`left`: everything so far becomes the left side of this operation.",
             _C7_S1_FULL,
             "    left = binary(t.op, left, right.expr);\n    t = peek(p);\n  }\n  return { ok: true, expr: left };\n}\n\nfunction parse(",
             _C7_S1_TESTS,
             ["The operator is `t.op`; the right side is `right.expr`.",
              "What goes on the left? Everything parsed so far.",
              "After rebuilding `left`, look at the next token again, so the loop can decide.",
              "`left = binary(t.op, left, right.expr); t = peek(p);` — then close the loop and return the tree."]),
    ],
    quiz=[
        _pq("Why does `parseProduct` use `peek` in the loop condition and `advance` inside?",
            ["It must look at the token to decide whether it belongs to this level, and only take it once it knows it does",
             "`advance` cannot be used in a condition",
             "`peek` is faster",
             "No reason; either works"],
            0,
            "Taking a token that belongs to another level loses it for good."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — the loop that leans left.
# ---------------------------------------------------------------------------

_C7_S2 = _pstep(
    "left", "The loop that leans left",
    "Associativity comes from the loop — and recursing into your own level gets it backwards.",
    """
There is another way to write `parseProduct` that looks at least as natural:

```ts
// product = primary ( ("*" | "/") product )?     ← recursion instead of a loop
advance(p);
const right = parseProduct(p);           // the rest of the chain, recursively
```

Parse one primary; if there is an operator, parse *the whole rest of the chain*
as the right side. It handles any length of chain, it is shorter, and for `*` it
even gives the right answer. It is wrong.

For `8 / 4 / 2` it builds:

```
(/ 8 (/ 4 2))       8 / (4 / 2)  =  4       ← recursion: leans right
(/ (/ 8 4) 2)       (8 / 4) / 2  =  1       ← the loop: leans left
```

Recursing on your own level for the right operand makes every chain
right-associative. Division and subtraction are left-associative, so the answer
is silently wrong — and for `*` and `+` it happens to be silently *right*, which
is how the bug survives until someone divides twice.

### Why the loop gets it right

Each time round, the loop takes **everything built so far** and makes it the
*left* side of the new operation:

```
left = 8
left = (/ 8 4)            ← the 8 went left
left = (/ (/ 8 4) 2)      ← the whole (/ 8 4) went left
```

So the earliest operation ends up deepest, and gets worked out first — which is
what "left to right" means. The operand on the right is always a *single*
primary, never the rest of the chain. That is the rule to remember:

> In a left-associative level, the right operand comes from the level **above**,
> never from your own.
""",
    """
```bash
$ echo '8 / 4 / 2' | node calc.ts
(/ (/ 8 4) 2)
$ echo '6 / 3 * 2' | node calc.ts
(* (/ 6 3) 2)
```

`6 / 3 * 2` is 4, not 1: `*` and `/` share a level, so they too go left to right.
""",
    pitfalls=[
        "Recursing into the same level for the right operand. Right-associative chains: `8 / 4 / 2` means `8 / (4 / 2)`.",
        "Testing only with `+` and `*`. Both associativities give the same answers for them, so no test can tell the correct parser from the wrong one.",
        "Believing `*` binds tighter than `/`. They are one level; `6 / 3 * 2` is `(6 / 3) * 2`.",
        "Building `binary(t.op, right.expr, left)` — sides swapped. `8 / 4` becomes `(/ 4 8)`.",
    ],
    warmup=[
        _pq("A parser builds `(- 10 (- 4 3))` for `10 - 4 - 3`. What did it probably do?",
            ["Parsed its own level recursively for the right operand, instead of looping",
             "Used `peek` instead of `advance`",
             "Nothing wrong — that is the correct tree",
             "Put `-` at a higher precedence than `-`"],
            0,
            "Right-leaning chains are the fingerprint of recursion on the same "
            "level."),
    ],
    exercises=[
        _pfix("calc-m7-left-fix1", "Eight divided by four divided by two",
              "`8 / 4 / 2` parses to `(/ 8 (/ 4 2))` — which is 4. The answer is 1. "
              "Multiplication chains look fine, which is why nobody noticed.",
              _c7(product=_C7_PRODUCT.replace(
                  "    const right = parsePrimary(p);", "    const right = parseProduct(p);")),
              _C7_FULL,
              _C7_TESTS,
              ["Which function parses the right operand of a `/`?",
               "It parses the whole rest of the chain, so the chain leans right.",
               "The right operand of a left-associative operator is one operand from the level above.",
               "`const right = parsePrimary(p);`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why can't a test suite of only `+` and `*` expressions catch an associativity bug?",
            ["`+` and `*` give the same answer grouped either way, so the wrong tree evaluates correctly",
             "Because `+` and `*` are right-associative",
             "Because such parsers do not build trees",
             "It can"],
            0,
            "Test the operators where the grouping changes the answer: `-` and `/`."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — two levels.
# ---------------------------------------------------------------------------

_C7_S3 = _pstep(
    "sum", "Two levels, one calling the other",
    "`parseSum` asks `parseProduct` for its operands — and `1 + 2 * 3` comes out right.",
    """
Now the second level. It is the same function with different operators, and one
more difference that is the entire point:

```ts
function parseSum(p: Parser): ParseResult {
  const first = parseProduct(p);
  …
  while (t.kind === "op" && (t.op === "+" || t.op === "-")) {
    advance(p);
    const right = parseProduct(p);
    …
    left = binary(t.op, left, right.expr);
    t = peek(p);
  }
  …
}
```

Its operands come from **`parseProduct`**, not `parsePrimary`. Walk `1 + 2 * 3`:

```
parseSum
  parseProduct            → reads 1, sees +, not its operator, returns 1
  sees +, advances
  parseProduct            → reads 2, sees *, advances, reads 3,
                            sees eof, returns (* 2 3)
  left = (+ 1 (* 2 3))
  sees eof, returns
```

The `+` never had to know about the `*`. It asked for "a product" and got one,
and a product is allowed to contain multiplications. That is precedence: **a
tighter operator is simply parsed further down the call chain**, so its nodes end
up further down the tree.

And `parse` now starts at the bottom of the ladder:

```ts
const result = parseSum(p);
```

### Why the loose operator is the outer function

It feels backwards at first: `*` is "more important", but `parseSum` runs first.
Remember module 5's rule — *the operation that happens last is at the top*. `+`
happens last, so its node is built last, by the outermost function, after
everything beneath it has been built by the functions it called.
""",
    """
```bash
$ echo '1 + 2 * 3' | node calc.ts
(+ 1 (* 2 3))
$ echo '1 * 2 + 3' | node calc.ts
(+ (* 1 2) 3)
$ echo '2 * 3 + 4 * 5' | node calc.ts
(+ (* 2 3) (* 4 5))
```

Look at the second line. The `*` came first in the text and is still underneath
the `+`. Reading order and tree order have come apart, which is exactly right.
""",
    pitfalls=[
        "The levels swapped: `parseSum` handling `* /` and calling a `parseProduct` that handles `+ -`. Everything still parses — into `(* (+ 1 2) 3)` for `1 + 2 * 3`.",
        "`parseSum` calling `parsePrimary` for its right operand. `1 + 2 * 3` then fails at the `*`, because nothing after a `+` is allowed to be a product.",
        "`parse` still starting at `parseProduct`. Every sum is refused with `unexpected '+'`.",
        "Adding a third copy of the loop for `-`. Operators of equal precedence share a level and a loop.",
    ],
    warmup=[
        _pq("In `1 + 2 * 3`, which function builds the `*` node?",
            ["`parseProduct`, called by `parseSum` to get the right operand of the `+`",
             "`parseSum`",
             "`parsePrimary`",
             "`parse`"],
            0,
            "The `+` asked for a product; the product contained a `*`."),
    ],
    exercises=[
        _pex("calc-m7-sum-1", "Ask the level above",
             "In `parseSum`'s loop, parse the right operand of the `+` or `-`. It "
             "is allowed to contain multiplications.",
             _C7_FULL,
             "    const right = parseProduct(p);\n    if (!right.ok) {\n      return right;\n    }\n    left = binary(t.op, left, right.expr);\n    t = peek(p);\n  }\n  return { ok: true, expr: left };\n}\n\nfunction parse(",
             _C7_TESTS,
             ["The operand of a `+` is a product, not a bare primary.",
              "Pass a failure up; otherwise grow `left` and peek again.",
              "`const right = parseProduct(p);` then the same four lines as `parseProduct`'s loop body."]),
        _pfix("calc-m7-sum-fix1", "The levels are upside down",
              "`1 + 2 * 3` parses to `(* (+ 1 2) 3)` — which is 9. Every "
              "expression parses without error, into the wrong tree.",
              _c7(product=_C7_PRODUCT.replace('(t.op === "*" || t.op === "/")', '(t.op === "+" || t.op === "-")'),
                  sum_=_C7_SUM.replace('(t.op === "+" || t.op === "-")', '(t.op === "*" || t.op === "/")')),
              _C7_FULL,
              _C7_TESTS,
              ["Which operators does `parseProduct` handle? Which does `parseSum`?",
               "The function further down the call chain builds nodes further down the tree.",
               "Tighter operators — `*` and `/` — belong to the level that is called, not the one that calls.",
               "Swap the two conditions back."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why is the function for the LOWEST-precedence operators the one `parse` calls first?",
            ["Its operators happen last, so its nodes are at the top of the tree, built after everything beneath them",
             "Because `+` comes first in the alphabet",
             "Because lower precedence means faster",
             "It is not; `parse` calls `parsePrimary` first"],
            0,
            "Outermost call, top of the tree, last to be worked out."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — what the ladder rejects.
# ---------------------------------------------------------------------------

_C7_S4 = _pstep(
    "errors", "What the ladder rejects",
    "Where each malformed input fails, and why every failure still reads sensibly.",
    """
The error messages were written in module 6 for a grammar of one number. They
still read correctly for this one, because each failure happens at the point
where a real person would say something was wrong:

| Input | Where it fails | Message |
|---|---|---|
| `1 +` | `parseSum` asks for a product, which asks for a primary, which gets `eof` | `error: unexpected end of input` |
| `* 2` | the very first primary gets `*` | `error: unexpected '*'` |
| `1 + * 2` | the primary after `+` gets `*` | `error: unexpected '*'` |
| `1 2` | `parseSum` stops at `2` (not its operator); the end check finds it | `error: unexpected '2'` |

Notice that no level reports anything about the tokens it *declines*. When
`parseProduct` sees a `+`, it is not an error — it just stops, and its caller
takes over. Only two places ever fail: a primary that cannot start, and the end
check that finds leftovers. Two failure points for a whole grammar is a very good
sign.

### The whole parser, as a ladder

```
parse          → parseSum, then expect eof
parseSum       → parseProduct ( ("+"|"-") parseProduct )*
parseProduct   → parsePrimary ( ("*"|"/") parsePrimary )*
parsePrimary   → number
```

Each rung only knows the rung directly above it. Module 8 adds a rung for unary
minus, and gives `parsePrimary` a way back to the bottom of the ladder.
Module 14 adds a rung underneath `parseSum` for `<` and `>`. Neither touches the
rungs it does not sit next to.
""",
    """
```bash
$ echo '1 +' | node calc.ts
error: unexpected end of input
$ echo '1 + * 2' | node calc.ts
error: unexpected '*'
$ echo '1 2' | node calc.ts
error: unexpected '2'
```

Every one fails at the first token that could not be part of an expression.
""",
    pitfalls=[
        "Making a level fail when it sees an operator it does not handle. `parseProduct` would then reject the `+` in `2 * 3 + 1` before `parseSum` ever saw it.",
        "A separate error for `1 +` like `missing operand`. It is tempting and it is one more message to keep consistent; `unexpected end of input` already says it.",
        "Checking for `eof` inside `parseSum`. The end check belongs to `parse`, once — a sum inside brackets (module 8) must be allowed to end at `)`.",
    ],
    warmup=[
        _pq("How many places in the parser can produce an error, after this module?",
            ["Two: a primary that cannot start with the token it got, and the end check in `parse`",
             "One per operator",
             "One per level",
             "Every `peek`"],
            0,
            "Levels decline tokens silently; only the primary and the end check "
            "complain."),
    ],
    exercises=[
        _pch("calc-m7-errors-sum", "The addition level", "Medium",
             "Write `parseSum` from nothing: a product, then any number of `+` or "
             "`-` followed by another product, building a left-leaning tree.",
             _C7_FULL,
             _C7_SUM.rstrip("\n"),
             _C7_TESTS,
             ["It is `parseProduct` with two changes. Which two?",
              "Its operands come from `parseProduct`, and its operators are `+` and `-`.",
              "Pass every failure up with `if (!x.ok) { return x; }`.",
              "Loop: peek, check, advance, parse the right side, rebuild `left`, peek again."]),
    ],
    quiz=[
        _pq("`parseProduct` sees a `+`. Why is that not an error?",
            ["It is not this level's operator, so the level stops and returns — the caller, `parseSum`, handles `+`",
             "Because `+` is valid everywhere",
             "It is an error",
             "Because the scanner already checked it"],
            0,
            "Each level declines what it does not handle. That is how the ladder "
            "composes."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C7_FINAL = _pch(
    "calc-m7-build", "Module 7 build — precedence", "Medium",
    "Write the two precedence levels and the `parse` that starts at the "
    "bottom of them:\n\n"
    "* `parseProduct` — primaries joined by `*` and `/`\n"
    "* `parseSum` — products joined by `+` and `-`\n"
    "* `parse` — a sum, then nothing but `eof`\n\n"
    "Both levels must lean left. `100 / 10 / 2` and `10 - 4 - 3` are in the "
    "tests for a reason.",
    _C7_FULL,
    _cjoin(_C7_PRODUCT, _C7_SUM, _C7_PARSE).rstrip("\n"),
    _C7_TESTS,
    ["Write `parseProduct` first: a primary, then a loop over `*` and `/`.",
     "`parseSum` is the same shape one level down, calling `parseProduct`.",
     "The right operand always comes from the level above — never your own level.",
     "`parse` calls `parseSum`, then checks for `eof` exactly as in module 6."],
)


_CALC_MODULES.append(_pmod(
    key="calc-precedence", number=7, phase="parse",
    title="Precedence, and why `1 + 2 * 3` is 7",
    what="two functions calling each other is the entire trick",
    goal="Parse `+ - * /` into a tree that binds them in the right order.",
    why=_C7_WHY,
    est_minutes=45,
    builds_on=["calc-tree", "calc-cursor"],
    concepts=["grammar rules", "recursive descent", "precedence levels",
              "left associativity", "loops vs recursion", "declining a token"],
    deliverable="`echo '1 + 2 * 3' | node calc.ts` prints `(+ 1 (* 2 3))`, and "
                "`10 - 4 - 3` prints `(- (- 10 4) 3)` — correct trees for any mix "
                "of the four operators.",
    objectives=[
        "Write a grammar rule for each precedence level, and read it aloud",
        "Turn a `( … )*` rule into a `while` loop that peeks to decide and advances to commit",
        "Explain why the right operand comes from the level above, and what recursing on your own level does",
        "Stack two levels so the looser operator's function calls the tighter one's",
        "Trace `1 + 2 * 3` through the calls and say which function builds each node",
        "Name the two places a parse can fail, and why levels decline tokens silently",
    ],
    brief=_C7_BRIEF,
    syntax=_C7_SYNTAX,
    steps=[_C7_S1, _C7_S2, _C7_S3, _C7_S4],
    final_build=_C7_FINAL,
    acceptance=[
        "`echo '1 + 2 * 3' | node calc.ts` prints `(+ 1 (* 2 3))`.",
        "`echo '1 * 2 + 3' | node calc.ts` prints `(+ (* 1 2) 3)`.",
        "`echo '10 - 4 - 3' | node calc.ts` prints `(- (- 10 4) 3)`, and `100 / 10 / 2` prints `(/ (/ 100 10) 2)`.",
        "`echo '1 +' | node calc.ts` prints `error: unexpected end of input`.",
        "`echo '1 2' | node calc.ts` prints `error: unexpected '2'`.",
        "The only functions that return a failure of their own are `parsePrimary` and `parse`.",
    ],
    manual_test="""
```bash
echo '1 + 2 * 3'       | node calc.ts     # (+ 1 (* 2 3))
echo '1 * 2 + 3'       | node calc.ts     # (+ (* 1 2) 3)
echo '2 * 3 + 4 * 5'   | node calc.ts     # (+ (* 2 3) (* 4 5))
echo '10 - 4 - 3'      | node calc.ts     # (- (- 10 4) 3)
echo '8 / 4 / 2'       | node calc.ts     # (/ (/ 8 4) 2)
echo '1 +'             | node calc.ts     # error: unexpected end of input
echo '1 + * 2'         | node calc.ts     # error: unexpected '*'
```

Now break it two ways, one at a time, and watch which inputs notice:

1. In `parseProduct`, change `const right = parsePrimary(p)` to
   `parseProduct(p)`. Run all seven. Only `8 / 4 / 2` changes — and it changes
   silently.
2. Put it back, and in `parse` call `parseProduct` instead of `parseSum`. Now
   every input with a `+` fails loudly.

A loud bug and a silent one. The silent one is why step 2 exists.
""",
    reference="""// calc.ts — module 7
//
// Precedence as a ladder of functions. Each precedence level is one function
// that loops over its own operators and asks the level ABOVE for its operands:
//
//   sum      = product ( ("+" | "-") product )*
//   product  = primary ( ("*" | "/") primary )*
//   primary  = number
//
// The loop makes each level left-associative: the tree built so far becomes the
// LEFT side of the next operation.
""" + _C7_FULL,
    stretch=[
        "Add `%` (remainder) at the same level as `*` and `/`. It should take one change to the scanner, one to `Op`, and one to a loop condition. Count how many places you actually touched.",
        "Add `**` for powers, binding tighter than `*`. It is RIGHT-associative: `2 ** 3 ** 2` is `2 ** 9`. Write its level with recursion on purpose — step 2's bug is this operator's correct behaviour.",
        "Collapse the two levels into one function, `parseLevel(p, ops, next)`… and find out that you cannot pass `parseProduct` as `next` without a callback type. What would the signature need to look like?",
        "Write the grammar for the language as it stands in a comment at the top of `calc.ts`, and keep it up to date for the rest of the project. It is the best documentation a parser can have.",
    ],
    glossary=[
        _pgloss("grammar", "Rules describing which sequences of tokens are valid and how they group. `sum = product ((\"+\" | \"-\") product)*`."),
        _pgloss("recursive descent", "Writing a parser as one function per grammar rule, each calling the functions for the rules it mentions."),
        _pgloss("precedence level", "A group of operators that bind equally tightly — `+ -` or `* /`. One function each."),
        _pgloss("left-associative", "Equal operators group from the left: `a - b - c` is `(a - b) - c`. Built with a loop that grows the left side."),
        _pgloss("declining a token", "A level that sees an operator it does not handle stops without error, leaving the token for its caller."),
    ],
    cheatsheet="""
```ts
// one function per level; operands come from the level ABOVE
function parseSum(p: Parser): ParseResult {
  const first = parseProduct(p);
  if (!first.ok) { return first; }
  let left = first.expr;
  let t = peek(p);
  while (t.kind === "op" && (t.op === "+" || t.op === "-")) {
    advance(p);                              // commit to the operator
    const right = parseProduct(p);           // NOT parseSum — that leans right
    if (!right.ok) { return right; }
    left = binary(t.op, left, right.expr);   // everything so far goes left
    t = peek(p);
  }
  return { ok: true, expr: left };
}
// parseProduct: same, with * / and parsePrimary.   parse: parseSum, then eof.
```

| Input | Tree |
|---|---|
| `1 + 2 * 3` | `(+ 1 (* 2 3))` |
| `1 * 2 + 3` | `(+ (* 1 2) 3)` |
| `8 / 4 / 2` | `(/ (/ 8 4) 2)` |
| `6 / 3 * 2` | `(* (/ 6 3) 2)` |

| Symptom | Cause |
|---|---|
| `(/ 8 (/ 4 2))` | right operand parsed by the same level (recursion) |
| `(* (+ 1 2) 3)` for `1 + 2 * 3` | levels swapped |
| every `+` unexpected | `parse` starts at `parseProduct` |
| loop never ends | no `t = peek(p)` at the bottom |
""",
    self_check=[
        "Can you write the grammar for `+ - * /` as two rules, and say which is the outer function?",
        "Can you trace `1 * 2 + 3` and say which function builds each node?",
        "Can you explain why `const right = parseProduct(p)` inside `parseProduct` makes chains lean right?",
        "Can you give an input where an associativity bug changes the answer, and one where it does not?",
        "Can you say why `parseProduct` does not fail when it sees a `+`?",
    ],
    review=[
        _pq("In recursive descent, what does each precedence level become?",
            ["A function that loops over its own operators and calls the next tighter level for operands",
             "A token kind",
             "A node kind",
             "A separate pass over the token list"],
            0,
            "One rule, one function, same shape."),
        _pq("`1 + 2 * 3`: why does the `*` end up beneath the `+`?",
            ["`parseSum` asks `parseProduct` for its right operand, and `parseProduct` consumes `2 * 3` whole",
             "Because `*` comes later in the text",
             "Because the scanner reorders tokens",
             "Because `show` prints it that way"],
            0,
            "Precedence is which function builds the node — and so how deep it is."),
        _pq("What makes `10 - 4 - 3` lean left?",
            ["The loop rebuilds `left = binary(op, left, right)`, so everything so far becomes the left side",
             "The scanner reads left to right",
             "Recursion into `parseSum` for the right operand",
             "`show` prints the left side first"],
            0,
            "Loop for left-associative, recursion for right-associative."),
        _pq("Why is there a bracket around `(t.op === \"+\" || t.op === \"-\")`?",
            ["`&&` binds tighter than `||`; without it the condition reads `(op and +) or -`, and a non-operator has no `op`",
             "Style only",
             "TypeScript requires brackets around every `||`",
             "To make it faster"],
            0,
            "The compiler refuses the unbracketed version — narrowing tells it "
            "`t.op` might not exist."),
        _pq("A parser passes every test with `+` and `*` in it, and builds `(/ 8 (/ 4 2))`. What should you add to the tests?",
            ["Chains of `-` and `/`, where grouping changes the answer",
             "Longer chains of `+`",
             "More whitespace",
             "Nothing; the tests pass"],
            0,
            "Test where the bug would show."),
    ],
    milestone="The parser understands precedence. `1 + 2 * 3` is an addition "
              "whose right-hand side is a multiplication, `10 - 4 - 3` leans left, "
              "and two functions — one calling the other — are the whole reason. "
              "Module 8 closes the grammar with brackets and unary minus.",
))
