# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 14 — Booleans and comparison.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses module 13's program.
#
# THE HARDEST MODULE IN PHASE 4, and the roadmap asked for it to be thought about
# first. What was settled:
#
#   * `type Value = number | boolean` gets a STEP OF ITS OWN (step 1), before
#     any token or node, because it is the change every layer feels. `typeof ` is
#     gated here and taught there.
#   * Three operators: `<`, `>`, `==`. One new precedence level, BELOW `+ -`
#     (so `1 + 1 == 2` compares a sum), left-associative like the rest — which
#     makes `1 < 2 < 3` a graded runtime TYPE error, not a parse error.
#   * `<` `>` and arithmetic need two numbers:
#         error: cannot apply '*' to a boolean
#     `==` needs two values of the SAME type:
#         error: cannot compare a number with a boolean
#     `-true` is `error: cannot apply '-' to a boolean`.
#   * `==` needs a one-character lookahead in the scanner (`=` vs `==`), the
#     first in the project. `===` is not an operator here.
#
# `arithmetic` BECOMES `apply`: it handles `==` first, then checks both operands
# are numbers, then switches — and the switch's `never` default still works,
# because the early return narrowed `"=="` out of `op`. Narrowing composes; the
# module shows it.
#
# THE COMPILER FORCES MOST OF THIS. `left * right` on two `Value`s does not
# compile, so "letting `true * 2` sneak through" is impossible to write by
# accident. The one check it cannot force is `==` across types (`===` accepts
# any two values), and that is the module's graded runtime fix.
# ---------------------------------------------------------------------------

_C14_TOKENS = """type Op = "+" | "-" | "*" | "/" | "<" | ">" | "==";

type NumberToken = { kind: "number"; value: number };
type BoolToken = { kind: "bool"; value: boolean };
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
  | BoolToken
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

function boolToken(value: boolean): BoolToken {
  return { kind: "bool", value: value };
}

""" + _C13_TOKENS[_C13_TOKENS.index("function opToken"):]

_C14_EQ = """    } else if (ch === "=") {
      if (src.charAt(i + 1) === "=") {
        tokens.push(opToken("=="));
        i = i + 2;
      } else {
        tokens.push(equalsToken());
        i = i + 1;
      }
"""

_C14_WORD = """      const word = src.slice(start, i);
      if (word === "let") {
        tokens.push(letToken());
      } else if (word === "true" || word === "false") {
        tokens.push(boolToken(word === "true"));
      } else {
        tokens.push(identToken(word));
      }
"""

_C14_SCAN = _C13_SCAN.replace(
    'ch === "+" || ch === "-" || ch === "*" || ch === "/")',
    'ch === "+" || ch === "-" || ch === "*" || ch === "/" || ch === "<" || ch === ">")', 1) \
    .replace('    } else if (ch === "=") {\n      tokens.push(equalsToken());\n      i = i + 1;\n', _C14_EQ, 1) \
    .replace(_C13_WORD, _C14_WORD, 1)

_C14_TREE = _C12_TREE.replace(
    'type Var = ', 'type BoolLit = { kind: "bool"; value: boolean };\ntype Var = ', 1) \
    .replace("type Expr = NumLit | Var | Neg | Binary;", "type Expr = NumLit | BoolLit | Var | Neg | Binary;", 1) \
    .replace("function variable(", 'function boolLit(value: boolean): BoolLit {\n  return { kind: "bool", value: value };\n}\n\nfunction variable(', 1)

_C14_DESCRIBE = _C13_DESCRIBE.replace(
    '    case "op":', '    case "bool":\n      return `\'${t.value}\'`;\n    case "op":', 1)

_C14_PRIMARY = _C12_PRIMARY.replace("  return parseSum(p);", "  return parseComparison(p);", 1) \
    .replace('  if (t.kind === "ident") {',
             '  if (t.kind === "bool") {\n    return { ok: true, expr: boolLit(t.value) };\n  }\n  if (t.kind === "ident") {', 1)

_C14_COMPARISON = _C7_SUM.replace("function parseSum(", "function parseComparison(", 1) \
    .replace("parseProduct(p)", "parseSum(p)") \
    .replace('(t.op === "+" || t.op === "-")', '(t.op === "<" || t.op === ">" || t.op === "==")', 1)

_C14_RESULT = """type Value = number | boolean;

type EvalResult = { ok: true; value: Value } | Failure;

function checked(value: number): EvalResult {
  if (!Number.isFinite(value)) {
    return { ok: false, error: "error: number too large" };
  }
  return { ok: true, value: value };
}
"""

_C14_ENV = "type Env = Map<string, Value>;\n"

_C14_EVAL = """function evaluate(e: Expr, env: Env): EvalResult {
  switch (e.kind) {
    case "num":
      return checked(e.value);
    case "bool":
      return { ok: true, value: e.value };
    case "var": {
      const value = env.get(e.name);
      if (value === undefined) {
        return { ok: false, error: `error: undefined variable '${e.name}'` };
      }
      return { ok: true, value: value };
    }
    case "neg": {
      const operand = evaluate(e.operand, env);
      if (!operand.ok) {
        return operand;
      }
      if (typeof operand.value !== "number") {
        return { ok: false, error: "error: cannot apply '-' to a boolean" };
      }
      return { ok: true, value: -operand.value };
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
      return apply(e.op, left.value, right.value);
    }
    default: {
      const impossible: never = e;
      return impossible;
    }
  }
}
"""

_C14_APPLY = """function apply(op: Op, left: Value, right: Value): EvalResult {
  if (op === "==") {
    if (typeof left !== typeof right) {
      return { ok: false, error: `error: cannot compare a ${typeof left} with a ${typeof right}` };
    }
    return { ok: true, value: left === right };
  }
  if (typeof left !== "number" || typeof right !== "number") {
    return { ok: false, error: `error: cannot apply '${op}' to a boolean` };
  }
  switch (op) {
    case "+":
      return checked(left + right);
    case "-":
      return checked(left - right);
    case "*":
      return checked(left * right);
    case "/":
      if (right === 0) {
        return { ok: false, error: "error: division by zero" };
      }
      return checked(left / right);
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


def _c14(tokens=_C14_TOKENS, scan=_C14_SCAN, describe=_C14_DESCRIBE, primary=_C14_PRIMARY,
         comparison=_C14_COMPARISON, evaluate=_C14_EVAL, apply=_C14_APPLY):
    return _stdin(_cjoin(tokens, _C6_RESULTS, _C4_UNEXPECTED, scan, _C14_TREE, _C13_STMTS,
                         _C6_STATE, describe, primary, _C8_UNARY, _C8_PRODUCT, _C7_SUM,
                         comparison, _C13_PARSE_STMT, _C13_PARSE_PROGRAM, _C14_RESULT,
                         _C14_ENV, evaluate, apply, _C13_EXECUTE, _C13_RUN_FN, _C13_MAIN))


_C14_FULL = _c14()

_C14_INPUTS = ["2 < 3", "3 < 2", "1 + 1 == 2", "let x = 4; x * x > 10", "10 / 4 > 2",
               "true", "false", "true == false", "true == true", "3 == 3",
               "1 < 2 == true", "let t = 1 > 0; t == true",
               "true * 2", "2 * true", "-true", "(1 < 2) + 1", "1 < 2 < 3",
               "1 == true", "true == 0", "2 = 2", "1 === 1", "let true = 1",
               "1 + 2 * 3", "let x = 1; x / (x - 1)"]
_C14_TESTS = _ctests(14, _C14_INPUTS)

# --- Step 1's plain program: a value that is one of two types ---------------
_C14_S1_MAIN = """type Value = number | boolean;

function doubled(v: Value): string {
  if (typeof v !== "number") {
    return "error: cannot apply '*' to a boolean";
  }
  return `${v * 2}`;
}

console.log(doubled(21));
console.log(doubled(true));
console.log(typeof 7);
console.log(typeof false);
console.log(`${1 < 2}`);
console.log(`${3 === 3}`);
"""
_C14_S1_OUT = "42\nerror: cannot apply '*' to a boolean\nnumber\nboolean\ntrue\ntrue"

_C14_WHY = (
    "Every value in the language so far has been a number, and every layer of "
    "`calc.ts` quietly assumes it: the environment maps names to numbers, "
    "`evaluate` returns one, `arithmetic` takes two. Comparison breaks that. "
    "`2 < 3` is not a number — it is `true` — and the moment a value can be "
    "`true`, `true * 2` becomes a program someone can write. JavaScript would "
    "answer `2`. A language that does is a language where a mistake turns into a "
    "wrong number three lines later. So this module changes what a value is, and "
    "then goes through every layer and makes it say what happens to the new kind "
    "— which is why the roadmap calls it the hardest in the phase."
)

_C14_BRIEF = """
### The whole module in one line

`let x = 4; x * x > 10` prints `true` — and `true * 2` prints `error: cannot
apply '*' to a boolean` instead of JavaScript's `2`.

### A value is not always a number

```ts
type Value = number | boolean;
```

That one line is the module. Everything else is following it through the layers:

| Layer | Change |
|---|---|
| scanner | `<`, `>`, `==` and the keywords `true`, `false` |
| parser | a `bool` node, and a comparison level below `+ -` |
| environment | `Map<string, Value>` — a name can hold a boolean |
| evaluator | returns a `Value`, and **every operation checks its operands** |

### The rules

| Expression | Result | Why |
|---|---|---|
| `2 < 3` | `true` | comparison of two numbers |
| `1 + 1 == 2` | `true` | `==` is looser than `+`, so the sum happens first |
| `true == false` | `false` | `==` works on two booleans too |
| `true * 2` | `error: cannot apply '*' to a boolean` | arithmetic needs numbers |
| `-true` | `error: cannot apply '-' to a boolean` | so does negation |
| `1 == true` | `error: cannot compare a number with a boolean` | `==` needs the same type on both sides |
| `1 < 2 < 3` | `error: cannot apply '<' to a boolean` | it is `(1 < 2) < 3` — a boolean compared with a number |

Until now every error in `calc.ts` was about the *text* (scanning, parsing) or
about *arithmetic*. These are **type errors**, found while running — the
program was well-formed and asked for something that does not make sense.

### `typeof`

JavaScript's `typeof v` is `"number"` or `"boolean"` for a `Value`, and
TypeScript narrows on it the way it narrows on a `kind` tag. It is how the
evaluator asks "is this a number?" — and the compiler insists that it asks:
`left * right` on two `Value`s does not compile.
"""

_C14_SYNTAX = [
    _syn(
        "type Value = number | boolean;",
        "A union of two primitive types. A `Value` is one or the other, and code "
        "that needs a number has to find out which first.",
        "",
        "Unlike `Token` or `Expr`, there is no `kind` tag — the two members are "
        "told apart by what they ARE, with `typeof`.",
    ),
    _syn(
        "if (typeof v !== \"number\") { … }",
        "`typeof x` is a string naming x's runtime type — `\"number\"`, "
        "`\"boolean\"`, `\"string\"`… Comparing it narrows, exactly like a tag.",
        """
function doubled(v: Value): string {
  if (typeof v !== "number") {
    return "error: cannot apply '*' to a boolean";   // v: boolean here
  }
  return `${v * 2}`;                                 // v: number here
}
""",
        "`typeof null` is `\"object\"` and `typeof []` is `\"object\"` — it is only "
        "precise for primitives. For `number | boolean` it is exact.",
    ),
    _syn(
        "`error: cannot compare a ${typeof left} with a ${typeof right}`",
        "`typeof` used as a value: its result is a string, so it can go straight "
        "into a message.",
        "",
        "",
    ),
    _syn(
        "if (src.charAt(i + 1) === \"=\") { … i = i + 2; }",
        "Look ONE character ahead to tell `==` from `=`, and consume both when it "
        "matches.",
        "",
        "`charAt` past the end is `\"\"`, which is not `\"=\"` — so a `=` at the very "
        "end of the source is safely an `equals`.",
    ),
    _syn(
        "return { ok: true, value: left < right };",
        "A comparison is an expression whose value is a boolean — it goes in the "
        "result like any other value.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — a value is not always a number.
# ---------------------------------------------------------------------------

_C14_S1 = _pstep(
    "value", "A value is not always a number",
    "`type Value = number | boolean`, `typeof`, and the check the compiler will not let you skip.",
    """
Start with the type, before any token or node, because it is the change every
layer will feel:

```ts
type Value = number | boolean;
```

`Token` and `Expr` were unions of objects with a `kind` tag. `Value` is a union
of two **primitive** types — there is no object to put a tag on. They are told
apart by what they are, with `typeof`:

```ts
typeof 7        // "number"
typeof false    // "boolean"
```

and TypeScript narrows on it exactly as it narrows on a tag:

```ts
function doubled(v: Value): string {
  if (typeof v !== "number") {
    return "error: cannot apply '*' to a boolean";   // v is boolean here
  }
  return `${v * 2}`;                                 // v is number here
}
```

### The compiler insists

Leave the check out and write `v * 2` on a `Value`:

```
error TS2362: The left-hand side of an arithmetic operation must be of type 'any', 'number', 'bigint' or an enum type.
```

This is the best news in the module. JavaScript would happily compute `true * 2`
— it is `2` — and the roadmap's worry was that `true * 2` might "sneak through".
With `Value` in the types, it cannot sneak: every arithmetic operation on a
`Value` refuses to compile until something has checked it is a number. The
evaluator does not have to remember to check. It has to *decide what the error
says*.

### What a comparison produces

```ts
1 < 2       // true — a boolean
3 === 3     // true
```

So `evaluate` has to be able to return one: its result becomes
`{ ok: true; value: Value }`, and the environment becomes `Map<string, Value>`, so
`let t = 1 > 0` can bind a boolean.
""",
    """
```
42
error: cannot apply '*' to a boolean
number
boolean
true
true
```

A number doubles; a boolean is refused by name; comparisons are booleans.
""",
    pitfalls=[
        "`typeof v === \"Number\"` — capitalised. It is always lowercase; the capitalised comparison is simply never true.",
        "A tag on values — `{ kind: \"num\", value: 1 }` — to tell them apart. It works, and it wraps every number in the program in an object for a question `typeof` already answers.",
        "Silencing TS2362 with `Number(v)`. `Number(true)` is `1`: exactly the `true * 2 = 2` this module exists to prevent.",
        "Forgetting the environment: `Map<string, number>` refuses `let t = 1 > 0`. Every place a value is stored has to widen.",
    ],
    warmup=[
        _pq("What does JavaScript itself say `true * 2` is?",
            ["`2` — `true` is converted to 1",
             "An error",
             "`NaN`",
             "`true`"],
            0,
            "Which is exactly why the language has to decide otherwise."),
    ],
    exercises=[
        _pex("calc-m14-value-1", "Is it a number?",
             "Finish `doubled`: a value that is not a number cannot be doubled.",
             _plain(_C14_S1_MAIN),
             '  if (typeof v !== "number") {',
             [("", _C14_S1_OUT)],
             ["`typeof v` is a string naming its type.",
              "After the check, `v * 2` must compile — so `v` must be a number.",
              "`if (typeof v !== \"number\") {`"]),
        _pex("calc-m14-value-2", "Two kinds of value",
             "Declare `Value`: a number or a boolean.",
             _plain(_C14_S1_MAIN),
             "type Value = number | boolean;",
             [("", _C14_S1_OUT)],
             ["A union of two primitive types.",
              "`type Value = number | boolean;`"]),
    ],
    quiz=[
        _pq("With `left: Value` and `right: Value`, why does `left * right` not compile?",
            ["Either might be a boolean, and `*` is only allowed on numbers — the compiler forces a check first",
             "Because `Value` is not a type",
             "Because `*` needs parentheses",
             "It does compile"],
            0,
            "The check `true * 2` needs cannot be forgotten."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — comparison in the scanner and the grammar.
# ---------------------------------------------------------------------------

_C14_S2 = _pstep(
    "compare", "Comparison in the scanner and the grammar",
    "`<`, `>`, `==` with a one-character lookahead, `true` and `false`, and a level below `+`.",
    """
### Tokens

`<` and `>` join the operator branch — `Op` grows to
`"+" | "-" | "*" | "/" | "<" | ">" | "=="`. `==` is the interesting one: the
scanner already turns `=` into an `equals` token for `let`. So at a `=` it looks
**one character ahead**:

```ts
} else if (ch === "=") {
  if (src.charAt(i + 1) === "=") {
    tokens.push(opToken("=="));
    i = i + 2;
  } else {
    tokens.push(equalsToken());
    i = i + 1;
  }
}
```

The first lookahead in the project. Consume two characters when it matches, one
when it does not. (`charAt` past the end is `""`, not `"="`, so a lone `=` at the
end of the source is still an `equals`.)

`true` and `false` are words, so they join `let` in the keyword check and become
a `bool` token carrying the value: `boolToken(word === "true")`. That also makes
them reserved: `let true = 1` is `expected a name but found 'true'`.

### A new level, below `+`

`1 + 1 == 2` should compare `2` with `2`, not add `1` to `1 == 2`. So comparison
binds **looser** than `+` — a new rung at the bottom of the ladder:

```
expr        =  comparison
comparison  =  sum ( ("<" | ">" | "==") sum )*
sum         =  product ( ("+" | "-") product )*
```

`parseComparison` is `parseSum` with different operators and `parseSum` for its
operands. And `parseExpr` — which module 8 introduced for exactly this day —
changes one line:

```ts
function parseExpr(p: Parser): ParseResult {
  return parseComparison(p);
}
```

Brackets, `let` values and statements all call `parseExpr`, so they all get
comparison without being touched.

### `1 < 2 < 3`

It parses — the level is left-associative like every other — as
`(1 < 2) < 3`, which is `true < 3`. That is a *type* error, reported by the
evaluator in step 4. Some languages forbid chained comparison in the grammar;
this one lets the type rules catch it, and the message says what went wrong.
""",
    """
```bash
$ echo '1 + 1 == 2' | node calc.ts
true
$ echo '10 / 4 > 2' | node calc.ts
true
$ echo '2 = 2' | node calc.ts
error: unexpected '='
```

A lone `=` is still `let`'s token, and has no business after an expression.
""",
    pitfalls=[
        "No lookahead: `==` scans as two `equals` tokens and `1 == 1` says `unexpected '='`.",
        "Comparison ABOVE `+`: `1 + 1 == 2` becomes `1 + (1 == 2)`, which is a type error.",
        "Changing the bracket case in `parsePrimary` to call `parseComparison` directly instead of changing `parseExpr`. It works, and it is exactly the scattered change `parseExpr` was invented to avoid.",
        "Treating `===` as an operator. This language has one equality, `==`; `1 === 1` is `==` followed by a stray `=`.",
    ],
    warmup=[
        _pq("Where does comparison sit on the precedence ladder, and why?",
            ["Below `+ -` — so `1 + 1 == 2` compares two sums",
             "Above `* /`",
             "Between `+` and `*`",
             "At the same level as `+`"],
            0,
            "Looser than arithmetic, as in almost every language."),
    ],
    exercises=[
        _pfix("calc-m14-compare-fix1", "Equals equals",
              "`1 + 1 == 2` says `error: unexpected '='`. So does `3 == 3`. A single "
              "`=` in a `let` still works.",
              _c14(scan=_C14_SCAN.replace(_C14_EQ,
                                          '    } else if (ch === "=") {\n      tokens.push(equalsToken());\n      i = i + 1;\n')),
              _C14_FULL,
              _C14_TESTS,
              ["How does the scanner handle a `=`?",
               "It never checks whether a second `=` follows.",
               "Look at `src.charAt(i + 1)`: if it is `=`, push `opToken(\"==\")` and move two."],
              difficulty="Easy"),
        _pex("calc-m14-compare-1", "The loosest operators",
             "Write the loop condition for `parseComparison`: the next token is "
             "`<`, `>` or `==`.",
             _C14_FULL,
             'while (t.kind === "op" && (t.op === "<" || t.op === ">" || t.op === "==")) {',
             _C14_TESTS,
             ["Module 7's condition, with three operators.",
              "`t.kind === \"op\"` first, then which one, bracketed.",
              "`while (t.kind === \"op\" && (t.op === \"<\" || t.op === \">\" || t.op === \"==\")) {`"]),
    ],
    quiz=[
        _pq("Why did adding the comparison level change only one line of the existing parser?",
            ["Everything that means \"a whole expression\" calls `parseExpr`, and only `parseExpr` had to point at the new bottom rung",
             "Because comparison is not a real level",
             "Because the parser is generated",
             "It changed every function"],
            0,
            "Module 8's indirection, paying out six modules later."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — booleans in the tree.
# ---------------------------------------------------------------------------

_C14_S3 = _pstep(
    "bool", "Booleans in the tree",
    "A `bool` node, a primary for `true` and `false`, and the compiler's list of switches.",
    """
`true` is a literal, like `7`. It gets a node and a primary of its own:

```ts
type BoolLit = { kind: "bool"; value: boolean };
type Expr = NumLit | BoolLit | Var | Neg | Binary;
```

```ts
if (t.kind === "bool") {
  return { ok: true, expr: boolLit(t.value) };
}
```

and evaluating one is as easy as evaluating a number:

```ts
case "bool":
  return { ok: true, value: e.value };
```

No `checked` — a boolean cannot overflow.

### The list

Add `BoolToken` and `BoolLit`, widen `Op`, compile — and module 10 hands you
the to-do list:

```
Type 'BoolToken' is not assignable to type 'never'.         describe
Type 'BoolLit' is not assignable to type 'never'.           evaluate
Type '"<" | ">" | "=="' is not assignable to type 'never'.  arithmetic
```

Three switches, three messages, each naming exactly what is new. Compare that
with module 8, where adding two tokens broke `describe` and nothing said so.
`describe` gets `case "bool": return `'${t.value}'`;` — which prints `'true'` —
and the other two are the next step.
""",
    """
```bash
$ echo 'true' | node calc.ts
true
$ echo 'let true = 1' | node calc.ts
error: expected a name but found 'true'
```

A boolean is a value on its own, and a reserved word in a `let`.
""",
    pitfalls=[
        "Treating `true` as a variable pre-set in the environment. `let true = 0` could then change it — and some languages have had exactly that bug.",
        "Putting a boolean through `checked`. It does not compile (`checked` takes a number), and there is nothing to check.",
        "Tagging the node `\"boolean\"` in one place and `\"bool\"` in another. The tag is compared as a string; pick one.",
    ],
    warmup=[
        _pq("After adding `BoolToken`, `BoolLit` and three operators, how many `never` errors appear?",
            ["Three — one each in `describe`, `evaluate` and `arithmetic`",
             "None",
             "One",
             "Seven"],
            0,
            "One per switch that has something new to handle."),
    ],
    exercises=[
        _pex("calc-m14-bool-1", "A literal truth",
             "In `parsePrimary`, turn a `bool` token into a boolean node.",
             _C14_FULL,
             '  if (t.kind === "bool") {\n    return { ok: true, expr: boolLit(t.value) };\n  }',
             _C14_TESTS,
             ["Same shape as the number and name cases.",
              "The factory is `boolLit`, and the token carries `value`.",
              "`if (t.kind === \"bool\") { return { ok: true, expr: boolLit(t.value) }; }`"]),
        _pex("calc-m14-bool-2", "Evaluating a boolean",
             "Add `evaluate`'s case for a boolean literal.",
             _C14_FULL,
             '    case "bool":\n      return { ok: true, value: e.value };',
             _C14_TESTS,
             ["It is its own value.",
              "No `checked`: that is for numbers.",
              "`case \"bool\": return { ok: true, value: e.value };`"]),
    ],
    quiz=[
        _pq("Why are `true` and `false` keywords rather than variables in the environment?",
            ["So they cannot be rebound — `let true = 0` is a parse error, not a redefinition",
             "Because the Map cannot hold booleans",
             "For speed",
             "No reason"],
            0,
            "A literal should mean the same thing everywhere."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — every operation checks its operands.
# ---------------------------------------------------------------------------

_C14_S4 = _pstep(
    "check", "Every operation checks its operands",
    "`apply`: `==` on matching types, everything else on numbers — and narrowing that composes.",
    """
`arithmetic` becomes `apply`, because it now does more than arithmetic. It takes
two `Value`s and decides, in order:

```ts
function apply(op: Op, left: Value, right: Value): EvalResult {
  if (op === "==") {
    if (typeof left !== typeof right) {
      return { ok: false, error: `error: cannot compare a ${typeof left} with a ${typeof right}` };
    }
    return { ok: true, value: left === right };
  }
  if (typeof left !== "number" || typeof right !== "number") {
    return { ok: false, error: `error: cannot apply '${op}' to a boolean` };
  }
  switch (op) {
    case "+": …
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
```

1. **`==`** works on two numbers or two booleans — but not one of each.
2. **Everything else** needs two numbers. After that `if`, both `left` and
   `right` are narrowed to `number`, so `left * right` compiles.

### Narrowing composes

Look at the switch. It has no `case "=="`, and its `never` check still compiles.
That is because the early `return` for `==` already narrowed `op`: by the time
the switch runs, `op` is `"+" | "-" | "*" | "/" | "<" | ">"`. Every narrowing
the compiler has seen on the way down is still in force. The two checks — one
for the operator, one for the operands — stack.

### The check the compiler cannot force

Arithmetic on an unchecked `Value` does not compile. `left === right` on two
`Value`s **does** — `===` accepts any two values — and says `1 === true` is
`false`. That is a real answer, and the wrong one for this language: comparing a
number with a boolean is almost certainly a mistake, and the user should hear
about it. This is the one type rule the evaluator has to *remember* rather than
be forced into, which is why it is the one graded as a bug.

### Negation too

```ts
if (typeof operand.value !== "number") {
  return { ok: false, error: "error: cannot apply '-' to a boolean" };
}
```

Module 8 made `-3` a `neg` node rather than `0 - 3`. Here is the payoff: negation
can say *negation* was misused, with its own `'-'`.
""",
    """
```bash
$ echo 'true * 2' | node calc.ts
error: cannot apply '*' to a boolean
$ echo '1 == true' | node calc.ts
error: cannot compare a number with a boolean
$ echo '1 < 2 < 3' | node calc.ts
error: cannot apply '<' to a boolean
$ echo 'let x = 4; x * x > 10' | node calc.ts
true
```

The phase's promise — variables, statements and booleans, evaluated in order.
""",
    pitfalls=[
        "`==` with no type check: `1 == true` quietly prints `false`. It compiles, which is why it is easy to miss.",
        "Checking operand types before handling `==`. Then `true == false` is refused as \"cannot apply '==' to a boolean\".",
        "Coercing instead of refusing — `Number(left)`. `true * 2` becomes `2`: JavaScript's answer, which this module exists to reject.",
        "One message for everything: `error: type error`. The operator and the type are what let the user find the mistake.",
    ],
    warmup=[
        _pq("After `if (op === \"==\") { … return … }`, why does the switch not need `case \"==\"`?",
            ["The early return narrowed `op`; `\"==\"` is no longer in its type, so the `never` check is satisfied without it",
             "Because `==` is not an operator",
             "Because the switch has a default",
             "It does need it"],
            0,
            "Narrowings stack. The switch sees what is left."),
    ],
    exercises=[
        _pex("calc-m14-check-1", "Two numbers, or a refusal",
             "In `apply`, after `==` is handled: if either operand is not a "
             "number, fail with `error: cannot apply '<op>' to a boolean`.",
             _C14_FULL,
             '  if (typeof left !== "number" || typeof right !== "number") {\n    return { ok: false, error: `error: cannot apply \'${op}\' to a boolean` };\n  }',
             _C14_TESTS,
             ["Two `typeof` checks joined by `||`.",
              "After this `if`, both must be numbers — the switch below depends on it.",
              "The message names the operator in quotes."]),
        _pfix("calc-m14-check-fix1", "A number equal to a boolean",
              "`1 == true` prints `false`. It should be refused: comparing a "
              "number with a boolean is a mistake, not a question with an answer. "
              "`true == false` and `3 == 3` must keep working.",
              _c14(apply=_C14_APPLY.replace(
                  "    if (typeof left !== typeof right) {\n      return { ok: false, error: `error: cannot compare a ${typeof left} with a ${typeof right}` };\n    }\n", "")),
              _C14_FULL,
              _C14_TESTS,
              ["Why does this compile, when `true * 2` without a check does not?",
               "`===` accepts any two values. The rule has to be written, not forced.",
               "Before comparing, check `typeof left !== typeof right` and fail with `error: cannot compare a ${typeof left} with a ${typeof right}`."],
              difficulty="Medium"),
    ],
    quiz=[
        _pq("Which type rule in this module does the COMPILER not force you to write?",
            ["`==` needing matching types — `===` compiles for any two values",
             "Arithmetic needing numbers",
             "Negation needing a number",
             "`<` needing numbers"],
            0,
            "Know which guarantees are forced and which are remembered."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C14_FINAL = _pch(
    "calc-m14-build", "Module 14 build — two kinds of value", "Hard",
    "Write the evaluator for a language with two kinds of value:\n\n"
    "* `evaluate` — cases for `num`, `bool`, `var`, `neg` and `binary`; "
    "negation refuses a boolean\n"
    "* `apply` — `==` on two values of the same type; everything else on two "
    "numbers, with division by zero and `checked` as before; `<` and `>` "
    "produce booleans\n\n"
    "Messages: `error: cannot apply '<op>' to a boolean` and `error: cannot "
    "compare a <type> with a <type>`. `1 < 2 < 3` is in the tests.",
    _C14_FULL,
    _cjoin(_C14_EVAL, _C14_APPLY).rstrip("\n"),
    _C14_TESTS,
    ["`evaluate` is module 13's with a `bool` case and a `typeof` check in `neg`.",
     "`apply` handles `==` first, then refuses non-numbers, then switches.",
     "`typeof left` is a string — it can go straight into the message.",
     "Keep the `never` default on both switches; `apply`'s works because `==` returned early."],
)


_CALC_MODULES.append(_pmod(
    key="calc-booleans", number=14, phase="lang",
    title="Booleans and comparison",
    what="the value type stops being `number`, and every layer notices",
    goal="Evaluate `2 < 3` without letting `true * 2` sneak through.",
    why=_C14_WHY,
    est_minutes=55,
    builds_on=["calc-precedence", "calc-never", "calc-arithmetic", "calc-statements"],
    concepts=["value types", "typeof narrowing", "runtime type errors",
              "one-character lookahead", "precedence levels", "narrowing composes",
              "forced vs remembered checks"],
    deliverable="`echo 'let x = 4; x * x > 10' | node calc.ts` prints `true`, and "
                "`echo 'true * 2'` is a reported error rather than `2`.",
    objectives=[
        "Widen the value type to `number | boolean`, and follow it through every layer",
        "Narrow a primitive union with `typeof`, and say why arithmetic on an unchecked `Value` does not compile",
        "Scan `==` with a one-character lookahead, and keywords `true` and `false`",
        "Add a comparison level below `+`, changing only `parseExpr` above it",
        "Write operand checks for every operator, and say which one the compiler does not force",
        "Explain why `1 < 2 < 3` is a type error here, not a parse error",
    ],
    brief=_C14_BRIEF,
    syntax=_C14_SYNTAX,
    steps=[_C14_S1, _C14_S2, _C14_S3, _C14_S4],
    final_build=_C14_FINAL,
    acceptance=[
        "`echo '2 < 3' | node calc.ts` prints `true`.",
        "`echo 'let x = 4; x * x > 10' | node calc.ts` prints `true`.",
        "`echo '1 + 1 == 2' | node calc.ts` prints `true` — comparison is looser than `+`.",
        "`echo 'true * 2' | node calc.ts` prints `error: cannot apply '*' to a boolean`, never `2`.",
        "`echo '1 == true' | node calc.ts` prints `error: cannot compare a number with a boolean`.",
        "`echo '-true' | node calc.ts` prints `error: cannot apply '-' to a boolean`.",
        "`echo 'let true = 1' | node calc.ts` is a parse error.",
    ],
    manual_test="""
```bash
echo '2 < 3'                   | node calc.ts     # true
echo '1 + 1 == 2'              | node calc.ts     # true
echo 'let x = 4; x * x > 10'   | node calc.ts     # true
echo 'let t = 1 > 0; t == true'| node calc.ts     # true
echo 'true * 2'                | node calc.ts     # cannot apply '*' to a boolean
echo '1 == true'               | node calc.ts     # cannot compare a number with a boolean
echo '1 < 2 < 3'               | node calc.ts     # cannot apply '<' to a boolean
echo '1 === 1'                 | node calc.ts     # unexpected '='
```

Then the experiment that shows what the types bought. In `apply`, delete the
`typeof … !== "number"` check and compile: every arithmetic case is now an error,
because `left * right` on two `Value`s is not allowed. Put it back. Now delete
the `typeof left !== typeof right` check inside the `==` branch and compile: no
error at all. Run `echo '1 == true'` — `false`. One rule the compiler forced, one
it could not.
""",
    reference="""// calc.ts — module 14
//
// A value is `number | boolean`. Comparisons (< > ==) sit on a new level below
// + -, and produce booleans; `true` and `false` are keywords.
//
// Type rules, checked while evaluating:
//   * arithmetic, < and > need two numbers  -> cannot apply '*' to a boolean
//   * negation needs a number               -> cannot apply '-' to a boolean
//   * == needs two values of the same type  -> cannot compare a number with a boolean
// The compiler forces the first two (arithmetic on a Value does not compile).
// The third it cannot force — `===` accepts anything — so it is written by hand.
""" + _C14_FULL,
    stretch=[
        "Add `<=`, `>=` and `!=`. Each needs a lookahead in the scanner; decide what `!` on its own means (it is unexpected, for now).",
        "Add `and` and `or` as keywords with a level below comparison. Then make them SHORT-CIRCUIT: `false and 1 / 0` should be `false`, not a division error. What does that require of `evaluate`?",
        "Allow chained comparison — `1 < 2 < 3` meaning `1 < 2 and 2 < 3` — the way Python does. Where does the change go: the parser, or the evaluator?",
        "Make `==` between a number and a boolean `false` instead of an error, and write down the argument for each design. Which one catches more mistakes?",
    ],
    glossary=[
        _pgloss("value type", "The set of kinds a value can be. Here, `number | boolean`."),
        _pgloss("typeof", "A JavaScript operator giving a value's runtime type as a string. TypeScript narrows on it."),
        _pgloss("runtime type error", "An operation applied to the wrong kind of value, found while evaluating a well-formed program. `true * 2`."),
        _pgloss("lookahead", "Looking at the next character (or token) to decide what the current one means, without consuming it. `=` vs `==`."),
        _pgloss("coercion", "Silently converting a value to another type — JavaScript's `true * 2 = 2`. This language refuses instead."),
    ],
    cheatsheet="""
```
comparison  =  sum ( ("<" | ">" | "==") sum )*     ← new bottom rung; parseExpr points here
```

```ts
type Value = number | boolean;

// scanner: one character of lookahead
if (src.charAt(i + 1) === "=") { tokens.push(opToken("==")); i = i + 2; }
else { tokens.push(equalsToken()); i = i + 1; }

function apply(op: Op, left: Value, right: Value): EvalResult {
  if (op === "==") {
    if (typeof left !== typeof right) { /* cannot compare a … with a … */ }
    return { ok: true, value: left === right };
  }
  if (typeof left !== "number" || typeof right !== "number") { /* cannot apply '…' */ }
  switch (op) { /* + - * / < > — "==" already narrowed away */ }
}
```

| Input | Output |
|---|---|
| `1 + 1 == 2` | `true` |
| `true * 2` | `error: cannot apply '*' to a boolean` |
| `-true` | `error: cannot apply '-' to a boolean` |
| `1 == true` | `error: cannot compare a number with a boolean` |
| `1 < 2 < 3` | `error: cannot apply '<' to a boolean` |

| Symptom | Cause |
|---|---|
| `1 == 1` → `unexpected '='` | no lookahead for `==` |
| `1 == true` → `false` | no type check in the `==` branch |
| `true == false` refused | operand check done before `==` is handled |
""",
    self_check=[
        "Can you list every layer that changed when `Value` stopped being `number`?",
        "Can you narrow a `number | boolean` with `typeof` and say what each branch sees?",
        "Can you explain why `==` needs a lookahead and `<` does not?",
        "Can you say where comparison sits on the ladder, and the one line that put it there?",
        "Can you explain why the switch in `apply` needs no `case \"==\"`?",
        "Can you name the one type rule the compiler does not force?",
    ],
    review=[
        _pq("What does `echo 'true * 2' | node calc.ts` print?",
            ["`error: cannot apply '*' to a boolean`",
             "`2`",
             "`true`",
             "`NaN`"],
            0,
            "JavaScript says 2. This language decided otherwise."),
        _pq("Why does `1 + 1 == 2` print `true`?",
            ["Comparison is a level below `+`, so both sums are computed before `==`",
             "Because `==` is evaluated first",
             "Because 1 + 1 is true",
             "It prints an error"],
            0,
            "One more rung, below the old bottom."),
        _pq("How does the scanner tell `=` from `==`?",
            ["It looks at the next character: `=` again means `==` (consume two), anything else means `equals`",
             "By the token after it",
             "The parser decides",
             "It cannot; spaces are required"],
            0,
            "The first one-character lookahead in the project."),
        _pq("Why is `1 < 2 < 3` an error rather than `true`?",
            ["It parses as `(1 < 2) < 3`, which compares a boolean with a number",
             "Because chained comparison is a syntax error",
             "Because 2 < 3 is false",
             "It prints `true`"],
            0,
            "Left associativity, then a type rule."),
        _pq("Why does TypeScript refuse `left * right` when both are `Value`?",
            ["Either could be a boolean; arithmetic needs numbers, so a `typeof` check must come first",
             "Because `Value` is an object",
             "Because `*` is reserved",
             "It does not refuse it"],
            0,
            "The compiler makes `true * 2` impossible to let through by accident."),
    ],
    milestone="Values are `number | boolean`, and every layer knows it. Comparisons "
              "produce booleans, arithmetic refuses them by name, and "
              "`let x = 4; x * x > 10` is `true` — the phase's promise, kept. "
              "Module 15 gives the language a way to use a boolean.",
))
