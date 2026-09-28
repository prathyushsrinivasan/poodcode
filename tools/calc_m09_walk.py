# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 9 — Walking the tree.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses module 8's scanner and parser.
#
# THE EASIEST MODULE IN THE PROJECT, AND IT SAYS SO. `evaluate` is a switch on
# the node kind that recurses into the children — about twenty lines — and it is
# that short because phase 2 guarantees every tree it is handed is correct.
# Saying that plainly is the module's argument.
#
# WHAT IS NOW LEGAL (`_CALC_SCOPE_RULES` at 9): `switch (` and `case `. Both
# `describe` (over Token) and the new `evaluate` (over Expr) are written as
# switches with a case per member and NO default — so the compiler already
# notices a missing case as "Function lacks ending return statement". Module 10
# explains where that accidental check stops working and replaces it with a
# deliberate one; this module only points at it.
#
# `show` LEAVES THE MAIN PROGRAM. The output is a number now, printed with a
# template literal (`${value}`) so `2.5` and `0.3333333333333333` print as JS
# prints them. `1 / 0` is NOT tested — it prints `Infinity`, and deciding what it
# should print is module 11's whole job. The brief flags it.
#
# `arithmetic(op, left, right)` is split out of `evaluate` now, so module 11 can
# make arithmetic fallible in one function and module 14 can add operators to
# it without touching the tree walk.
# ---------------------------------------------------------------------------

_C9_TREE = _C8_TREE.split("\nfunction show(")[0].rstrip("\n") + "\n"

_C9_DESCRIBE = """function describe(t: Token): string {
  switch (t.kind) {
    case "number":
      return `'${t.value}'`;
    case "op":
      return `'${t.op}'`;
    case "lparen":
      return "'('";
    case "rparen":
      return "')'";
    case "eof":
      return "end of input";
  }
}

function unexpectedToken(t: Token): Failure {
  return { ok: false, error: `error: unexpected ${describe(t)}` };
}

function expected(what: string, t: Token): Failure {
  return { ok: false, error: `error: expected ${what} but found ${describe(t)}` };
}
"""

_C9_EVAL = """function evaluate(e: Expr): number {
  switch (e.kind) {
    case "num":
      return e.value;
    case "neg":
      return -evaluate(e.operand);
    case "binary":
      return arithmetic(e.op, evaluate(e.left), evaluate(e.right));
  }
}
"""

_C9_ARITH = """function arithmetic(op: Op, left: number, right: number): number {
  switch (op) {
    case "+":
      return left + right;
    case "-":
      return left - right;
    case "*":
      return left * right;
    case "/":
      return left / right;
  }
}
"""

_C9_RUN = _C6_RUN.replace("  return show(parsed.expr);", "  return `${evaluate(parsed.expr)}`;")


def _c9(describe=_C9_DESCRIBE, evaluate=_C9_EVAL, arith=_C9_ARITH, run=_C9_RUN):
    return _stdin(_cjoin(_C8_TOKENS, _C6_RESULTS, _C4_UNEXPECTED, _C8_SCAN, _C9_TREE,
                         _C6_STATE, describe, _C8_PRIMARY, _C8_UNARY, _C8_PRODUCT,
                         _C7_SUM, _C8_PARSE, evaluate, arith, run))


_C9_FULL = _c9()

_C9_INPUTS = ["1 + 2 * 3", "(1 + 2) * 3", "10 / 4", "-4 + 10", "(1 + 2) * -3",
              "10 - 4 - 3", "100 / 10 / 2", "1 / 3", "2 * -3 - -3", "7",
              "8 / (4 / 2)", "1 +", "1 $ 2", "(1 + 2", "1 + )"]
_C9_TESTS = _ctests(9, _C9_INPUTS)

_C9_WHY = (
    "The parser builds a tree that is always right or says why it could not. "
    "Now the tree has to become an answer. This is the moment the whole project "
    "has been building towards — text in, a number out — and it is the shortest "
    "module in it, because walking a correct tree is a switch on the kind of "
    "node and a recursive call for each child. The work was in getting the tree "
    "right. This module collects the reward, and learns the `switch` statement "
    "that every function over a union in this project will be written with from "
    "now on."
)

_C9_BRIEF = """
### The whole module in one line

`evaluate(e)` — a `switch` on the node's kind, a recursive call for each child,
and a number out. `echo '1 + 2 * 3' | node calc.ts` prints `7`.

### It is easy, and that is the point

```ts
function evaluate(e: Expr): number {
  switch (e.kind) {
    case "num":
      return e.value;
    case "neg":
      return -evaluate(e.operand);
    case "binary":
      return arithmetic(e.op, evaluate(e.left), evaluate(e.right));
  }
}
```

That is the evaluator. Precedence is not in it — the tree already put `2 * 3`
underneath the `+`, so evaluating the `+` *has to* evaluate the product first.
Brackets are not in it — they are not in the tree. Associativity is not in it.
Every hard thing about arithmetic was decided in phase 2, and this function just
follows the shape it was handed.

If this module feels too short, that feeling is the lesson: **the right data
structure turns the next step into bookkeeping.**

### `switch`, and why now

Up to now, every function over a union was an `if` chain ending in a
fall-through. Module 8 showed what that costs: `describe` answered "end of
input" for a bracket, and nothing said a word. A `switch` with one `case` per
member names every kind out loud — and, as step 1 shows, the compiler already
notices when one is missing. Module 10 turns that noticing into a guarantee.

### What prints

```
$ echo '10 / 4' | node calc.ts
2.5
$ echo '1 / 3' | node calc.ts
0.3333333333333333
```

Numbers are JavaScript numbers, printed the way JavaScript prints them. One input
is left alone on purpose: try `1 / 0`. What it prints is not a decision this
language made — it is one JavaScript made for you — and module 11 is where that
changes.
"""

_C9_SYNTAX = [
    _syn(
        "switch (e.kind) { case \"num\": … }",
        "Run the branch whose `case` matches the value. Switching on a union's "
        "tag narrows `e` inside each case, exactly as an `if` would.",
        """
switch (t.kind) {
  case "number":
    return `'${t.value}'`;     // here t is a NumberToken
  case "eof":
    return "end of input";     // here t is an EofToken
}
""",
        "Each case here ends in `return`, which also leaves the `switch`. A case "
        "that does not return or `break` runs straight into the next one — a "
        "classic bug that `return` in every case makes impossible.",
    ),
    _syn(
        "case \"binary\": return arithmetic(e.op, evaluate(e.left), evaluate(e.right));",
        "A case that recurses: evaluate each child, then combine the two numbers.",
        "",
        "The children are evaluated first, left then right — so the deepest "
        "operations happen first, which is what their depth in the tree meant.",
    ),
    _syn(
        "switch (op) { case \"+\": … case \"/\": … }",
        "Switching on a union of string literals. Same narrowing, no object "
        "needed.",
        "",
        "",
    ),
    _syn(
        "`${evaluate(parsed.expr)}`",
        "A number turned into text by a template literal — `7`, `2.5`, "
        "`0.3333333333333333`, as JavaScript writes them.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — switch.
# ---------------------------------------------------------------------------

_C9_S1 = _pstep(
    "switch", "One case per kind",
    "`switch` and `case`, narrowing inside each case — and `describe` rewritten so every kind is named.",
    """
`describe` from module 8 is an `if` chain ending in a fall-through. Rewrite it
with the statement built for exactly this:

```ts
function describe(t: Token): string {
  switch (t.kind) {
    case "number":
      return `'${t.value}'`;
    case "op":
      return `'${t.op}'`;
    case "lparen":
      return "'('";
    case "rparen":
      return "')'";
    case "eof":
      return "end of input";
  }
}
```

`switch (t.kind)` looks at the tag once; each `case` is one possible value.
Inside `case "number":`, `t` is a `NumberToken` and `t.value` exists; inside
`case "op":`, `t.op` does. Narrowing works exactly as it did for `if`.

### There is no fall-through line

The old version said "everything else is the end of input". This one names
`eof` like every other kind. There is no "everything else", because every member
of `Token` has its own case.

### And the compiler is already watching

Delete the `case "rparen":` lines and compile:

```
error TS2366: Function lacks ending return statement and return type does not include 'undefined'.
```

The compiler worked out that the cases cover every kind *except* `rparen`, so for
a `)` the function would reach its closing brace without returning. It is not the
clearest message in the world — it points at the return type, not at the missing
case — but it is the compiler catching exactly the bug from module 8. Module 10
is about when this accidental check stops working, and what replaces it.

### `return` ends the case

Every case here ends in `return`, which leaves the whole function. A `case` that
does not end in `return` (or `break`) carries on into the next case's code. In
this project every case returns, and that bug cannot happen.
""",
    """
```bash
$ echo '1 + )' | node calc.ts
error: unexpected ')'
$ echo '(1 + 2' | node calc.ts
error: expected ')' but found end of input
```

The same messages as module 8 — `describe` changed shape, not behaviour.
""",
    pitfalls=[
        "A `case` with no `return` or `break`: execution runs on into the next case. Always end a case, and in this project always with `return`.",
        "Adding `default: return \"end of input\";`. It compiles — and it is the fall-through again, switching the compiler's check off.",
        "Switching on `t` instead of `t.kind`. A `case` compares with `===`, and no token object is `=== \"number\"`.",
        "Writing `case \"number\" || \"op\":`. That is one case whose value is `\"number\"`. Two kinds sharing code need two `case` lines stacked.",
    ],
    warmup=[
        _pq("In `case \"op\":`, what type does `t` have?",
            ["`OpToken` — the switch narrows on the tag, like an `if`",
             "`Token`",
             "`string`",
             "`OpToken | EofToken`"],
            0,
            "Each case is a narrowed view of the union."),
    ],
    exercises=[
        _pex("calc-m9-switch-1", "Name the closing bracket",
             "Finish `describe`'s case for a closing bracket.",
             _C9_FULL,
             '    case "rparen":\n      return "\')\'";',
             _C9_TESTS,
             ["One `case` line with the tag value, then a `return`.",
              "The bracket is shown in single quotes, like every token the user typed.",
              "`case \"rparen\": return \"')'\";`"]),
        _pex("calc-m9-switch-2", "Switch on the tag",
             "Write the line that opens `describe`'s switch: it chooses a case by "
             "the token's kind.",
             _C9_FULL,
             "  switch (t.kind) {\n    case \"number\":\n      return `'${t.value}'`;",
             _C9_TESTS,
             ["`switch (…) {` with the value to compare in the brackets.",
              "Compare the tag, not the token.",
              "`switch (t.kind) {` — then the first case, for numbers."]),
    ],
    quiz=[
        _pq("You delete one `case` from `describe`'s switch. Why does it stop compiling?",
            ["The remaining cases no longer cover every kind, so the function could reach its end without returning a string",
             "Because `switch` requires every case",
             "Because the deleted kind is still used",
             "It still compiles"],
            0,
            "An accidental exhaustiveness check. Module 10 makes it deliberate."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — evaluate.
# ---------------------------------------------------------------------------

_C9_S2 = _pstep(
    "evaluate", "Recurse, then combine",
    "`evaluate`: a number is itself, a negation is minus its operand, a binary is its children combined.",
    """
Three kinds of node, three cases:

```ts
function evaluate(e: Expr): number {
  switch (e.kind) {
    case "num":
      return e.value;
    case "neg":
      return -evaluate(e.operand);
    case "binary":
      return arithmetic(e.op, evaluate(e.left), evaluate(e.right));
  }
}
```

- A **number** is already its own value. The base case — no recursion.
- A **negation** is minus whatever its operand evaluates to.
- A **binary** evaluates its left side, then its right side, then combines the
  two numbers with its operator.

This is `show` from module 5 with numbers where strings were. Same shape,
because it is the same tree: handle one node, trust the recursion for the rest.

### Following `1 + 2 * 3`

```
evaluate (+ 1 (* 2 3))
  evaluate 1         → 1
  evaluate (* 2 3)
    evaluate 2       → 2
    evaluate 3       → 3
    2 * 3            → 6
  1 + 6              → 7
```

The multiplication happened first — not because `evaluate` knows anything about
precedence, but because it is *deeper*, and a node cannot be combined until its
children are values. Phase 2 put it there. Phase 3 just walks down and back up.
""",
    """
```bash
$ echo '1 + 2 * 3' | node calc.ts
7
$ echo '(1 + 2) * 3' | node calc.ts
9
$ echo '(1 + 2) * -3' | node calc.ts
-9
```

The tree from module 8, now with a value at the top.
""",
    pitfalls=[
        "`case \"neg\": return -e.operand;` — negating a tree, not a number. It does not compile; the operand has to be evaluated first.",
        "Evaluating the right side before the left. For arithmetic the result is the same; in module 12, when evaluation can fail, it decides which error is reported.",
        "Adding precedence rules to `evaluate`. If it needs them, the tree is wrong — fix the parser.",
        "Evaluating `e.left` twice (once to check, once to use). Harmless now, expensive later, and wrong the day evaluation has side effects.",
    ],
    warmup=[
        _pq("Why does `evaluate` compute `2 * 3` before the `+` in `1 + 2 * 3`?",
            ["The `*` node is a child of the `+` node, and a node's children must be values before it can be combined",
             "`evaluate` checks precedence",
             "Because `*` is evaluated first alphabetically",
             "It does not"],
            0,
            "Depth is order. The parser chose the depth."),
    ],
    exercises=[
        _pex("calc-m9-evaluate-1", "Combine two children",
             "Finish the `binary` case: evaluate both sides, then combine them "
             "with the node's operator.",
             _C9_FULL,
             "      return arithmetic(e.op, evaluate(e.left), evaluate(e.right));",
             _C9_TESTS,
             ["`arithmetic` takes an operator and two numbers.",
              "The sides are trees. What turns a tree into a number?",
              "`return arithmetic(e.op, evaluate(e.left), evaluate(e.right));`"]),
        _pex("calc-m9-evaluate-2", "Minus a whole expression",
             "Finish the `neg` case: the value is minus whatever the operand is "
             "worth.",
             _C9_FULL,
             "      return -evaluate(e.operand);",
             _C9_TESTS,
             ["The operand is an `Expr`, not a number.",
              "Evaluate it, then negate the result.",
              "`return -evaluate(e.operand);`"]),
    ],
    quiz=[
        _pq("Which case of `evaluate` is the base case?",
            ["`num` — it returns without evaluating anything else",
             "`binary`",
             "`neg`",
             "There is none"],
            0,
            "Every tree bottoms out in numbers, so every evaluation finishes."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — the arithmetic.
# ---------------------------------------------------------------------------

_C9_S3 = _pstep(
    "arithmetic", "Four operators, one switch",
    "`arithmetic(op, left, right)` — and why it lives in a function of its own.",
    """
```ts
function arithmetic(op: Op, left: number, right: number): number {
  switch (op) {
    case "+":
      return left + right;
    case "-":
      return left - right;
    case "*":
      return left * right;
    case "/":
      return left / right;
  }
}
```

A switch on a union of string literals — `Op` — rather than on an object's tag.
Same narrowing, same rule that every member gets a case, and the same compile
error if one is missing.

### Why not inline it in `evaluate`

It would fit. It is separate because the next two phases change *this* part and
not the tree walk:

- **Module 11** makes arithmetic able to fail — `1 / 0` — and that change
  belongs to division, not to the switch over node kinds.
- **Module 14** adds `<`, `>` and `==` to `Op`. They go here, as three more
  cases, and `evaluate` does not change at all.

Keeping "how to walk a tree" and "what an operator does" in different functions
means each change touches one of them.

### Order still matters

`left - right`, not `right - left`. The tree remembered which side was which
(module 5); the parser put the first operand on the left (module 7); this is the
last place that order could be thrown away.
""",
    """
```bash
$ echo '10 - 4 - 3' | node calc.ts
3
$ echo '100 / 10 / 2' | node calc.ts
5
$ echo '10 / 4' | node calc.ts
2.5
```

`3` and `5` are the left-leaning trees paying off; a right-leaning parser would
print `9` and `20`.
""",
    pitfalls=[
        "`right - left`. Every subtraction and division comes out inverted, and every addition and multiplication hides it.",
        "Integer division: expecting `10 / 4` to be `2`. JavaScript has one number type, and `/` is real division.",
        "A `default: return 0;` \"just in case\". It hides the missing-case error, and module 14 adds three operators that would silently evaluate to 0.",
    ],
    warmup=[
        _pq("Why is `arithmetic` a separate function from `evaluate`?",
            ["Later modules change what operators do (division failing, new comparison operators) without changing how the tree is walked",
             "Functions cannot contain two switches",
             "For speed",
             "No reason"],
            0,
            "Separate reasons to change, separate functions."),
    ],
    exercises=[
        _pfix("calc-m9-arithmetic-fix1", "Ten minus four is minus six",
              "`10 - 4` prints `-6` and `8 / 2` prints `0.25`. Additions and "
              "multiplications are all correct.",
              _c9(arith=_C9_ARITH.replace("left - right", "right - left").replace("left / right", "right / left")),
              _C9_FULL,
              _C9_TESTS + _ctests(9, ["10 - 4", "8 / 2"]),
              ["Which operators are wrong? What do they have in common?",
               "For `+` and `*` the order of the operands does not matter.",
               "The left operand comes first: `left - right`, `left / right`."],
              difficulty="Intro"),
        _pex("calc-m9-arithmetic-1", "Division",
             "Finish the last case of `arithmetic`.",
             _C9_FULL,
             '    case "/":\n      return left / right;',
             _C9_TESTS,
             ["A `case` for the `/` operator.",
              "Which operand is divided by which?",
              "`case \"/\": return left / right;`"]),
    ],
    quiz=[
        _pq("A `default: return 0;` is added to `arithmetic`. What goes wrong later?",
            ["An operator added to `Op` without a case silently evaluates to 0 instead of failing to compile",
             "Nothing; defaults are always good",
             "Division stops working",
             "It does not compile"],
            0,
            "A default is a fall-through with a different keyword. Module 10 is "
            "about what to put there instead."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — text in, a number out.
# ---------------------------------------------------------------------------

_C9_S4 = _pstep(
    "answer", "Text in, a number out",
    "`run` gains its third stage, and `calc.ts` is a working calculator.",
    """
`run` from module 6 had two stages. It gets its third in one line:

```ts
function run(src: string): string {
  const scanned = scan(src);
  if (!scanned.ok) {
    return scanned.error;
  }
  const parsed = parse(scanned.tokens);
  if (!parsed.ok) {
    return parsed.error;
  }
  return `${evaluate(parsed.expr)}`;
}
```

`evaluate` does not return a result union, because — so far — evaluating a
correct tree cannot fail. Every tree it can be handed has numbers at every leaf
and one of four operators at every branch. (Hold that thought.)

`show` is no longer called. Keep it in your own `calc.ts` if you like — it is
the best debugging tool this project has, and the stretch list has a way to
bring it back behind a flag.

### The pipeline, finished

```
"1 + 2 * 3"  →  scan  →  [1, +, 2, *, 3, eof]  →  parse  →  (+ 1 (* 2 3))  →  evaluate  →  7
```

Phase 3's promise was *text in, a number out*. That is now true.

### The thought you were holding

```bash
$ echo '1 / 0' | node calc.ts
Infinity
$ echo '0 / 0' | node calc.ts
NaN
```

The language never decided that. JavaScript did, and this calculator repeated it
without looking. `Infinity` then flows into anything that uses it — `1 / 0 - 1 /
0` is `NaN` — and the user who typed a zero by mistake gets a word that describes
nothing they wrote. Module 11 decides what dividing by zero *means* here. First,
module 10 makes sure that adding things to the language cannot quietly break
what you just built.
""",
    """
```bash
$ echo '1 + 2 * 3' | node calc.ts
7
$ echo '(1 + 2) * -3' | node calc.ts
-9
$ echo '1 / 3' | node calc.ts
0.3333333333333333
$ echo '1 +' | node calc.ts
error: unexpected end of input
```

A calculator. Errors from the first two stages still come through unchanged.
""",
    pitfalls=[
        "`console.log` inside `evaluate`. The value goes back to `run`, which returns it; there is still exactly one `console.log` in the program.",
        "Rounding the output. `1 / 3` is `0.3333333333333333` in this language, as it is in JavaScript; hiding digits is a display decision for a later stretch, not the evaluator's.",
        "Evaluating before checking the parse result. `parsed.expr` does not exist until `parsed.ok` is checked — the compiler holds you to it.",
    ],
    warmup=[
        _pq("Why does `evaluate` return a plain `number` rather than a result union?",
            ["Every tree the parser can produce evaluates to a number — nothing can go wrong yet",
             "Because evaluation is too fast to fail",
             "Result unions only work for parsers",
             "It should; this is a bug"],
            0,
            "\"Yet\". Module 11 finds the thing that can."),
    ],
    exercises=[
        _pch("calc-m9-answer-run", "Three stages, one function", "Easy",
             "Write `run`: scan, then parse, then evaluate — returning the first "
             "failure's message, or the value as text.",
             _C9_FULL,
             _C9_RUN.split("\n\nconsole.log")[0],
             _C9_TESTS,
             ["Module 6's `run` with one more line at the end.",
              "Each stage that can fail gets `if (!x.ok) { return x.error; }`.",
              "`evaluate` cannot fail — its number goes straight into a template literal.",
              "`return `${evaluate(parsed.expr)}`;`"]),
    ],
    quiz=[
        _pq("What does `echo '1 / 0' | node calc.ts` print after this module, and whose decision was it?",
            ["`Infinity` — JavaScript's decision, repeated without the language making one",
             "An error — the evaluator checks for zero",
             "`0`",
             "It crashes"],
            0,
            "Module 11 makes the decision on purpose."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C9_FINAL = _pch(
    "calc-m9-build", "Module 9 build — a calculator", "Medium",
    "Write the third stage and the function that runs all three:\n\n"
    "* `evaluate` — a `num` is its value, a `neg` is minus its operand, a "
    "`binary` combines its children\n"
    "* `arithmetic` — one `case` per operator\n"
    "* `run` — scan, parse, evaluate; the first failure's message, or the value\n\n"
    "No `default` in either switch. `10 - 4 - 3` and `100 / 10 / 2` are in the "
    "tests for a reason.",
    _C9_FULL,
    _cjoin(_C9_EVAL, _C9_ARITH, _C9_RUN.split("\n\nconsole.log")[0]).rstrip("\n"),
    _C9_TESTS,
    ["`evaluate`: `switch (e.kind)` with three cases.",
     "The binary case evaluates both children and hands the numbers to `arithmetic`.",
     "`arithmetic`: `switch (op)`, `left` before `right` for `-` and `/`."],
)
_CALC_MODULES.append(_pmod(
    key="calc-walk", number=9, phase="eval",
    title="Walking the tree",
    what="switch on the kind, recurse into the children, return a number",
    goal="Turn an `Expr` into the number it means.",
    why=_C9_WHY,
    est_minutes=30,
    builds_on=["calc-tree", "calc-parens"],
    concepts=["tree walking", "switch statements", "narrowing by case",
              "evaluation order", "separating walk from operation"],
    deliverable="`echo '1 + 2 * 3' | node calc.ts` prints `7`, and "
                "`(1 + 2) * -3` prints `-9` — `calc.ts` is a working calculator.",
    objectives=[
        "Write a `switch` over a union's tag with one `case` per member, and say what narrowing it does",
        "Read the compile error a missing case produces, and say what it is pointing at",
        "Write a recursive evaluator and trace it on `1 + 2 * 3`",
        "Explain why the evaluator contains no precedence rules",
        "Keep operator behaviour in its own function, and say which later modules that protects",
        "Name the input whose output the language has not yet decided",
    ],
    brief=_C9_BRIEF,
    syntax=_C9_SYNTAX,
    steps=[_C9_S1, _C9_S2, _C9_S3, _C9_S4],
    final_build=_C9_FINAL,
    acceptance=[
        "`echo '1 + 2 * 3' | node calc.ts` prints `7` — not `9`.",
        "`echo '(1 + 2) * -3' | node calc.ts` prints `-9`.",
        "`echo '10 / 4' | node calc.ts` prints `2.5`.",
        "`echo '10 - 4 - 3' | node calc.ts` prints `3`.",
        "Scan and parse errors print exactly as before.",
        "`describe` and `evaluate` are switches with a case per kind and no `default`; deleting any case stops `calc.ts` compiling.",
    ],
    manual_test="""
```bash
echo '1 + 2 * 3'      | node calc.ts     # 7
echo '(1 + 2) * 3'    | node calc.ts     # 9
echo '10 / 4'         | node calc.ts     # 2.5
echo '-4 + 10'        | node calc.ts     # 6
echo '(1 + 2) * -3'   | node calc.ts     # -9
echo '1 + )'          | node calc.ts     # error: unexpected ')'
```

Pipe something longer through it — `echo '((2 + 3) * (7 - 2)) / -5'` — and
check it by hand. Then two experiments:

1. Delete `case "neg":` and its line from `evaluate`, and run
   `npx tsc --noEmit --strict calc.ts`. Read the error: it names the function,
   not the case. Put it back.
2. Run `echo '1 / 0' | node calc.ts`. Decide what you think it *should* print,
   and write it down. Module 11 will ask.
""",
    reference="""// calc.ts — module 9
//
// Text in, a number out. The evaluator is a switch on the node kind that
// recurses into the children — short, because the parser guarantees every tree
// is correct. Precedence, brackets and associativity are all in the tree's
// shape; none of them appear here.
""" + _C9_FULL,
    stretch=[
        "Bring `show` back behind a prefix: an input starting `#tree ` prints the tree instead of evaluating it. When the answer is wrong, this is how you find out whether the parser or the evaluator is lying.",
        "Write `steps(e)`: evaluate the tree and print each operation as it happens — `2 * 3 = 6`, then `1 + 6 = 7`. The order it prints in is evaluation order; check it matches what you expect.",
        "Evaluate without recursion, using an explicit stack of nodes. It is much longer — which is an argument for the recursive version, and also how you would evaluate a tree too deep for the call stack (module 17 meets that problem).",
        "Round output to at most ten significant digits, so `0.1 + 0.2` prints `0.3`. Then argue with yourself about whether a calculator should hide that `0.1 + 0.2` is not `0.3`.",
    ],
    glossary=[
        _pgloss("evaluator", "The stage that turns a tree into a value by walking it."),
        _pgloss("tree walk", "Visiting every node of a tree, usually recursively, doing something at each."),
        _pgloss("switch statement", "Choose a branch by comparing one value against each `case`. On a union's tag, it narrows like an `if`."),
        _pgloss("post-order", "Children before their parent — the order an evaluator needs, since a node combines values its children produced."),
    ],
    cheatsheet="""
```ts
function evaluate(e: Expr): number {
  switch (e.kind) {
    case "num":    return e.value;                     // base case
    case "neg":    return -evaluate(e.operand);
    case "binary": return arithmetic(e.op, evaluate(e.left), evaluate(e.right));
  }
}

function arithmetic(op: Op, left: number, right: number): number {
  switch (op) {
    case "+": return left + right;
    case "-": return left - right;       // left first
    case "*": return left * right;
    case "/": return left / right;       // 1 / 0 → Infinity: module 11
  }
}

// run: scan → parse → `${evaluate(parsed.expr)}`
```

| Input | Output |
|---|---|
| `1 + 2 * 3` | `7` |
| `(1 + 2) * -3` | `-9` |
| `10 / 4` | `2.5` |
| `1 / 0` | `Infinity` — not yet decided |

| Symptom | Cause |
|---|---|
| `10 - 4` is `-6` | `right - left` |
| `TS2366: Function lacks ending return statement` | a `case` missing from a switch |
| code from the next case runs | a `case` with no `return` |
""",
    self_check=[
        "Can you write `evaluate` from memory, and say which case is the base case?",
        "Can you trace `(1 + 2) * -3` through `evaluate` and give the order operations happen in?",
        "Can you explain why there are no precedence rules in the evaluator?",
        "Can you say what the compiler reports when a case is missing, and what it points at?",
        "Can you say why `arithmetic` is its own function?",
    ],
    review=[
        _pq("Why is the evaluator so short?",
            ["The parser already encoded precedence, associativity and grouping in the tree's shape",
             "Because arithmetic is simple",
             "Because it uses `switch`",
             "Because it does not handle negation"],
            0,
            "The right data structure turns the next step into bookkeeping."),
        _pq("Inside `case \"binary\":`, why does `e.left` exist?",
            ["The switch narrowed `e` to `Binary` for that case",
             "Every `Expr` has `left`",
             "Because of `evaluate`'s return type",
             "It does not"],
            0,
            "Cases narrow exactly as `if` does."),
        _pq("`switch (e.kind)` has cases for `num` and `binary` but not `neg`. What happens?",
            ["Compile error: the function could reach its end without returning a number",
             "`neg` nodes evaluate to 0",
             "`neg` nodes evaluate to `undefined` silently",
             "Nothing"],
            0,
            "The accidental exhaustiveness check. Module 10: when it fails you."),
        _pq("What does `10 - 4 - 3` print, and which earlier module is responsible?",
            ["`3` — module 7's loop built the left-leaning tree `(- (- 10 4) 3)`",
             "`9` — module 9's evaluator",
             "`3` — module 9's evaluator reads left to right",
             "An error"],
            0,
            "The evaluator follows the shape; the parser chose it."),
    ],
    milestone="Phase 3's promise, kept: text in, a number out. `calc.ts` is a "
              "working calculator, the evaluator is twenty lines, and the reason it "
              "is twenty lines is everything phase 2 did. Module 10 makes sure it "
              "stays correct as the language grows.",
))
