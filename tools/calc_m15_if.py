# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 15 — `if` as an expression.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses module 14's program.
#
# THE PAYOFF MODULE. `if c then a else b` is an EXPRESSION with a value, so it
# goes anywhere a number can (`1 + if true then 2 else 3`), and — the type rule
# the roadmap names — `else` is MANDATORY, because an expression must always have
# a value. That also removes the dangling-else problem entirely.
#
# THE MODULE 10 TEST. Adding three token kinds and one node kind must produce a
# compile error in exactly the switches that need them — `describe` (three
# tokens) and `evaluate` (the node) — and nowhere else. Step 2 is built on that
# list, and its compile-time fix is deliberate: "if the compiler does not
# complain in exactly the right places, module 10 was not finished."
#
# DECIDED:
#   * `if` is a primary. Its condition and both branches are full expressions
#     (`parseExpr`), so the `else` branch reaches as far right as it can:
#     `if true then 1 else 2 + 10` is 1 — graded as a runtime fix.
#   * The condition must be a boolean: `error: if condition must be a boolean`.
#     No truthiness — `if 1 then …` is refused, consistent with module 14.
#   * ONLY THE CHOSEN BRANCH IS EVALUATED. `if false then 1 / 0 else 2` is 2. The
#     eager version is the module's other graded fix.
#   * Branches may have different types (`if c then 1 else true`) — the language
#     is dynamically typed, and the module says so rather than pretending.
# ---------------------------------------------------------------------------

_C15_TOKENS = _C14_TOKENS.replace(
    'type SemiToken = { kind: "semi" };\n',
    'type SemiToken = { kind: "semi" };\ntype IfToken = { kind: "if" };\ntype ThenToken = { kind: "then" };\ntype ElseToken = { kind: "else" };\n', 1) \
    .replace("  | SemiToken\n", "  | SemiToken\n  | IfToken\n  | ThenToken\n  | ElseToken\n", 1) \
    .replace("function lparenToken(",
             'function ifToken(): IfToken {\n  return { kind: "if" };\n}\n\n'
             'function thenToken(): ThenToken {\n  return { kind: "then" };\n}\n\n'
             'function elseToken(): ElseToken {\n  return { kind: "else" };\n}\n\n'
             "function lparenToken(", 1)

_C15_KEYWORDS = """      } else if (word === "if") {
        tokens.push(ifToken());
      } else if (word === "then") {
        tokens.push(thenToken());
      } else if (word === "else") {
        tokens.push(elseToken());
"""

_C15_SCAN = _C14_SCAN.replace(
    "        tokens.push(boolToken(word === \"true\"));\n",
    "        tokens.push(boolToken(word === \"true\"));\n" + _C15_KEYWORDS, 1)

_C15_TREE = _C14_TREE.replace(
    "type Binary = ",
    'type If = { kind: "if"; cond: Expr; whenTrue: Expr; whenFalse: Expr };\ntype Binary = ', 1) \
    .replace("type Expr = NumLit | BoolLit | Var | Neg | Binary;",
             "type Expr = NumLit | BoolLit | Var | Neg | If | Binary;", 1) \
    .replace("function binary(",
             "function ifExpr(cond: Expr, whenTrue: Expr, whenFalse: Expr): If {\n"
             '  return { kind: "if", cond: cond, whenTrue: whenTrue, whenFalse: whenFalse };\n'
             "}\n\nfunction binary(", 1)

_C15_DESCRIBE = _C14_DESCRIBE.replace(
    '    case "lparen":',
    '    case "if":\n      return "\'if\'";\n    case "then":\n      return "\'then\'";\n'
    '    case "else":\n      return "\'else\'";\n    case "lparen":', 1)

_C15_IF_PARSE = """  if (t.kind === "if") {
    const cond = parseExpr(p);
    if (!cond.ok) {
      return cond;
    }
    const thenTok = advance(p);
    if (thenTok.kind !== "then") {
      return expected("'then'", thenTok);
    }
    const whenTrue = parseExpr(p);
    if (!whenTrue.ok) {
      return whenTrue;
    }
    const elseTok = advance(p);
    if (elseTok.kind !== "else") {
      return expected("'else'", elseTok);
    }
    const whenFalse = parseExpr(p);
    if (!whenFalse.ok) {
      return whenFalse;
    }
    return { ok: true, expr: ifExpr(cond.expr, whenTrue.expr, whenFalse.expr) };
  }
"""

_C15_PRIMARY = _C14_PRIMARY.replace("  return unexpectedToken(t);\n}",
                                    _C15_IF_PARSE + "  return unexpectedToken(t);\n}", 1)

_C15_IF_EVAL = """    case "if": {
      const cond = evaluate(e.cond, env);
      if (!cond.ok) {
        return cond;
      }
      if (typeof cond.value !== "boolean") {
        return { ok: false, error: "error: if condition must be a boolean" };
      }
      if (cond.value) {
        return evaluate(e.whenTrue, env);
      }
      return evaluate(e.whenFalse, env);
    }
"""

_C15_EVAL = _C14_EVAL.replace("    default: {\n      const impossible: never = e;",
                              _C15_IF_EVAL + "    default: {\n      const impossible: never = e;", 1)


def _c15(tokens=_C15_TOKENS, scan=_C15_SCAN, tree=_C15_TREE, describe=_C15_DESCRIBE,
         primary=_C15_PRIMARY, evaluate=_C15_EVAL):
    return _stdin(_cjoin(tokens, _C6_RESULTS, _C4_UNEXPECTED, scan, tree, _C13_STMTS,
                         _C6_STATE, describe, primary, _C8_UNARY, _C8_PRODUCT, _C7_SUM,
                         _C14_COMPARISON, _C13_PARSE_STMT, _C13_PARSE_PROGRAM, _C14_RESULT,
                         _C14_ENV, evaluate, _C14_APPLY, _C13_EXECUTE, _C13_RUN_FN, _C13_MAIN))


_C15_FULL = _c15()

_C15_INPUTS = ["if 2 < 3 then 10 else 20", "if 2 > 3 then 10 else 20",
               "let x = 5; if x > 3 then x * 2 else 0", "1 + if true then 2 else 3",
               "if true then 1 else 2 + 10", "if false then 1 else 2 + 10",
               "if 1 > 2 then 1 else if 2 > 1 then 2 else 3",
               "let big = if 1 < 2 then true else false; big == true",
               "if false then 1 / 0 else 2", "if true then 1 / 0 else 2",
               "if (1 < 2) then (3) else (4)", "if true then true else 1",
               "if 1 then 2 else 3", "if true then 1", "if true 1 else 2", "then",
               "let if = 1", "if x then 1 else 2", "1 + 2 * 3"]
_C15_TESTS = _ctests(15, _C15_INPUTS)

_C15_WHY = (
    "The language can compare things and has nothing to do with the answer. "
    "`2 < 3` is `true`, and `true` just sits there. A language that can make a "
    "decision needs a conditional — and here it is an *expression*, with a value, "
    "so it can go anywhere a number can. That shape forces a rule: an expression "
    "must always produce a value, so the `else` is not optional. It is also the "
    "module that tests module 10. Adding `if` means new tokens and a new node, "
    "and if the compiler does not point at exactly the switches that must handle "
    "them, the exhaustiveness checks were not finished."
)

_C15_BRIEF = """
### The whole module in one line

`if 2 < 3 then 10 else 20` evaluates to `10` — a conditional that is an
expression, with a mandatory `else`, and only the chosen branch evaluated.

### An expression, not a statement

In most languages you have written, `if` is a statement: it *does* one thing or
another. Here it is an **expression**: it *is* one value or another.

```
let size = if n > 100 then 3 else 1;
1 + if flag then 2 else 3
```

That is why it can sit on the right of a `let` or inside a sum. It is a primary,
like a number or a bracketed expression.

### The type rule it forces

An expression must always have a value. An `if` without an `else` would have no
value when its condition is false — so **`else` is mandatory**:

```
$ echo 'if true then 1' | node calc.ts
error: expected 'else' but found end of input
```

A pleasant side effect: the *dangling else* problem — which `if` does this
`else` belong to? — cannot happen, because every `if` has exactly one.

### Three rules, decided

| Rule | Example |
|---|---|
| The condition must be a boolean | `if 1 then 2 else 3` → `error: if condition must be a boolean` |
| Only the chosen branch is evaluated | `if false then 1 / 0 else 2` → `2` |
| Each branch reaches as far right as it can | `if true then 1 else 2 + 10` → `1` |

### And the test module 10 has been waiting for

Three new tokens (`if`, `then`, `else`) and a new node (`If`). Add the types,
compile, and read the list. It should name `describe` for the tokens, `evaluate`
for the node — and nothing else. If it does, every switch in `calc.ts` is honest.
"""

_C15_SYNTAX = [
    _syn(
        "type If = { kind: \"if\"; cond: Expr; whenTrue: Expr; whenFalse: Expr };",
        "A node with three children: the condition and both branches. Every one "
        "is required — no optional `whenFalse`.",
        "",
        "Making `whenFalse` optional would be the type saying an `if` might have "
        "no value, which the language has decided it may not.",
    ),
    _syn(
        "if (cond.value) { return evaluate(e.whenTrue, env); }",
        "Evaluate ONE branch, chosen by the condition. The other is never looked "
        "at.",
        """
if (cond.value) {
  return evaluate(e.whenTrue, env);
}
return evaluate(e.whenFalse, env);
""",
        "After `typeof cond.value !== \"boolean\"` has returned, `cond.value` is a "
        "`boolean`, so it can be the `if` condition directly.",
    ),
    _syn(
        "return expected(\"'then'\", thenTok);",
        "Module 8's `expected`, for a keyword the grammar requires.",
        "",
        "",
        recap=True,
    ),
    _syn(
        "} else if (word === \"if\") { tokens.push(ifToken()); }",
        "One more keyword in the scanner's word check. `if`, `then` and `else` are "
        "reserved exactly as `let` and `true` are.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — a conditional with a value.
# ---------------------------------------------------------------------------

_C15_S1 = _pstep(
    "expression", "A conditional with a value",
    "`if … then … else …` as an expression, three keywords, and why `else` is not optional.",
    """
```
if 2 < 3 then 10 else 20
```

Three keywords, three expressions. The whole thing has a value — whichever branch
the condition picks — so it is an expression, and it can go anywhere an
expression can:

```
let x = if 2 < 3 then 10 else 20;      the value of a let
1 + if true then 2 else 3              an operand
(if a then b else c) * 2               inside brackets
```

### The keywords

`if`, `then` and `else` are words, so they join the scanner's keyword check —
after the whole word has been read, as module 13 established:

```ts
} else if (word === "if") {
  tokens.push(ifToken());
} else if (word === "then") {
  tokens.push(thenToken());
} else if (word === "else") {
  tokens.push(elseToken());
}
```

Three token kinds, each with no payload. All three are now reserved: `let if = 1`
is `expected a name but found 'if'`.

### Why `else` is mandatory

A statement can do nothing. An expression cannot *be* nothing. If `else` were
optional, `if false then 1` would have no value — and then `1 + if false then 1`
would have to mean something. There are languages that answer with a special
"no value" value; there are languages that make the `else` mandatory. This one is
the second, and the grammar enforces it:

```
primary  =  …  |  "if" expr "then" expr "else" expr
```

`then` is mandatory too. Some languages drop it and use brackets instead; here
the keyword is what tells the parser the condition has ended — without it,
`if a b` would not say where the condition stops.
""",
    """
```bash
$ echo 'let if = 1' | node calc.ts
error: expected a name but found 'if'
$ echo 'then' | node calc.ts
error: unexpected 'then'
```

Keywords are reserved, and a `then` on its own cannot start anything.
""",
    pitfalls=[
        "Recognising `if` by prefix — `iffy` is a name.",
        "An optional `else` that defaults to 0 or `false`. The condition's other outcome would silently have a value nobody wrote.",
        "Treating `if` as a statement. Then `let x = if …` is impossible, and a whole class of programs needs a temporary variable.",
    ],
    warmup=[
        _pq("Why must an `if` expression have an `else`?",
            ["An expression always has a value; without `else`, a false condition would leave it with none",
             "Because `then` needs a partner",
             "It is a scanner limitation",
             "It does not have to"],
            0,
            "The type rule the conditional forces."),
    ],
    exercises=[
        _pex("calc-m15-expression-1", "Three more keywords",
             "Extend the scanner's word check: `if`, `then` and `else` each become "
             "their own token.",
             _C15_FULL,
             _C15_KEYWORDS.rstrip("\n"),
             _C15_TESTS,
             ["Three more `else if` branches in the keyword check, before the name case.",
              "Compare the whole word.",
              "`} else if (word === \"if\") { tokens.push(ifToken()); }` — and the same for `then` and `else`."]),
    ],
    quiz=[
        _pq("Where can an `if` expression appear?",
            ["Anywhere an expression can — a `let`'s value, an operand, inside brackets",
             "Only at the start of a statement",
             "Only inside brackets",
             "Only after `let`"],
            0,
            "It is a primary."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — the node, and the list.
# ---------------------------------------------------------------------------

_C15_S2 = _pstep(
    "list", "The node, and the list",
    "An `If` node with three children — and the compiler naming exactly the switches that must learn about it.",
    """
```ts
type If = { kind: "if"; cond: Expr; whenTrue: Expr; whenFalse: Expr };
type Expr = NumLit | BoolLit | Var | Neg | If | Binary;
```

Three children, none optional — the type says what the grammar says.

### Module 10's final exam

Add the three token types to `Token`, the node to `Expr`, and compile *before*
writing anything else. You should get exactly this:

```
Type 'IfToken' is not assignable to type 'never'.       describe
Type 'ThenToken' is not assignable to type 'never'.     describe
Type 'ElseToken' is not assignable to type 'never'.     describe
Type 'If' is not assignable to type 'never'.            evaluate
```

Four errors, two functions, every one naming what is missing. And just as
important, **nothing else**: `apply` is not mentioned, because `Op` did not
change; `execute` is not mentioned, because `Stmt` did not. The compiler
complained in exactly the right places.

That is what module 10 was for. In module 8, two new tokens broke `describe`
silently. Here, four new types produce a complete, precise to-do list — and
`calc.ts` does not run until it is done.

`describe` gets three cases: `'if'`, `'then'`, `'else'`. `evaluate`'s case is
step 4.
""",
    """
```bash
$ npx tsc --noEmit --strict calc.ts
```

Clean — once `describe` has its three cases and `evaluate` has its one.
""",
    pitfalls=[
        "Adding a `default` to quiet the list. The list is the work.",
        "`whenFalse?: Expr`. It type-checks an `if` with no `else`, which the parser never builds and the evaluator would have to invent a value for.",
        "Naming the fields `then` and `else`. Legal as property names, and confusing to read beside the keywords of the same name.",
    ],
    warmup=[
        _pq("After adding `If` to `Expr`, why is `apply` NOT in the compiler's list?",
            ["`apply` switches on `Op`, which did not change",
             "Because `apply` has no default",
             "Because `if` is not an operator",
             "It is in the list"],
            0,
            "Exactly the right places — and only those."),
    ],
    exercises=[
        _pfix("calc-m15-list-fix1", "The node nobody evaluates",
              "This does not compile:\n\n"
              "    Type 'If' is not assignable to type 'never'.\n\n"
              "The parser builds `If` nodes. The evaluator has never heard of them.",
              _c15(evaluate=_C14_EVAL),
              _C15_FULL,
              _C15_TESTS,
              ["The error is in `evaluate`'s default.",
               "Add `case \"if\": { … }` before it.",
               "Evaluate the condition; refuse a non-boolean; evaluate whichever branch it picks."],
              difficulty="Medium"),
        _pex("calc-m15-list-1", "Describe the keywords",
             "Give `describe` its case for `then`.",
             _C15_FULL,
             '    case "then":\n      return "\'then\'";',
             _C15_TESTS,
             ["Like `let`: the keyword in single quotes.",
              "`case \"then\": return \"'then'\";`"]),
    ],
    quiz=[
        _pq("What does it prove when adding `If` produces errors in `describe` and `evaluate` only?",
            ["Every switch over `Token` and `Expr` has a `never` check, and no other code depends on those unions",
             "That the parser is wrong",
             "That `if` is a statement",
             "Nothing"],
            0,
            "Module 10, finished."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — parsing it.
# ---------------------------------------------------------------------------

_C15_S3 = _pstep(
    "parse", "Parsing `if`",
    "A primary with three full expressions — and how far the `else` reaches.",
    """
An `if` starts with its keyword, so it is recognised the way a bracket is: one
token decides.

```ts
if (t.kind === "if") {
  const cond = parseExpr(p);
  …
  const thenTok = advance(p);
  if (thenTok.kind !== "then") {
    return expected("'then'", thenTok);
  }
  const whenTrue = parseExpr(p);
  …
  const elseTok = advance(p);
  if (elseTok.kind !== "else") {
    return expected("'else'", elseTok);
  }
  const whenFalse = parseExpr(p);
  …
  return { ok: true, expr: ifExpr(cond.expr, whenTrue.expr, whenFalse.expr) };
}
```

All three parts are parsed with `parseExpr` — full expressions, comparisons
included, so `if x > 3 then …` works. The keywords tell each one where to stop:
`parseExpr` declines `then` and `else` (they are not operators), and hands them
back.

### How far the `else` reaches

The last part has no keyword after it, so it takes everything it can:

```
if true then 1 else 2 + 10     →    if true then 1 else (2 + 10)    →   1
```

The `else` branch is `2 + 10`, not `2`. This is what almost every language with
an `if` expression does, and it is what `parseExpr` gives for free. Parsing the
`else` branch with anything smaller — `parseUnary`, say — would make it
`(if true then 1 else 2) + 10`, which is `11`. Wrap it in brackets if that is
what you mean.

### Nesting

`else if` needs no special case: the `else` branch is an expression, and an `if`
is an expression.

```
if a then 1 else if b then 2 else 3     →     if a then 1 else (if b then 2 else 3)
```
""",
    """
```bash
$ echo 'if true then 1 else 2 + 10' | node calc.ts
1
$ echo 'if 1 > 2 then 1 else if 2 > 1 then 2 else 3' | node calc.ts
2
$ echo 'if true 1 else 2' | node calc.ts
error: expected 'then' but found '1'
```
""",
    pitfalls=[
        "Parsing a branch with a smaller rule than `parseExpr`. `if true then 1 else 2 + 10` becomes 11, and `if x > 3 then …` may fail at the `>`.",
        "`unexpectedToken` for a missing `then`. `expected 'then' but found '1'` tells the user what the grammar needed.",
        "A special `elseif` keyword. The `else` branch can already be an `if`.",
        "Putting `if` in `parseStatement`. Then it cannot be an operand, and `1 + if …` fails.",
    ],
    warmup=[
        _pq("What is `if false then 1 else 2 + 10`?",
            ["`12` — the `else` branch is `2 + 10`",
             "`2`",
             "`11`",
             "An error"],
            0,
            "The last branch reaches as far right as it can."),
    ],
    exercises=[
        _pex("calc-m15-parse-1", "Then what?",
             "After the condition, the next token must be `then`. Take it, and "
             "fail with `expected 'then'` if it is anything else.",
             _C15_FULL,
             '    const thenTok = advance(p);\n    if (thenTok.kind !== "then") {\n      return expected("\'then\'", thenTok);\n    }',
             _C15_TESTS,
             ["`advance` to take the token.",
              "Only a `then` token will do.",
              "`expected(\"'then'\", thenTok)` otherwise."]),
        _pfix("calc-m15-parse-fix1", "An `else` that stops too soon",
              "`if true then 1 else 2 + 10` prints `11`. The `+ 10` was meant to "
              "be part of the `else` branch — which the condition did not choose.",
              _c15(primary=_C15_PRIMARY.replace("    const whenFalse = parseExpr(p);",
                                                "    const whenFalse = parseUnary(p);")),
              _C15_FULL,
              _C15_TESTS,
              ["Which function parses the `else` branch?",
               "It parses only a unary — so the `+ 10` is left for the level above, which adds it to the whole `if`.",
               "Every part of an `if` is a full expression: `parseExpr`."],
              difficulty="Medium"),
    ],
    quiz=[
        _pq("Why does `parseExpr` stop at `then` inside the condition?",
            ["`then` is not an operator any level handles, so every level declines it and returns",
             "Because `parseExpr` looks for `then`",
             "Because the scanner splits there",
             "It does not stop"],
            0,
            "Module 7's rule: levels decline what they do not handle."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — only one branch runs.
# ---------------------------------------------------------------------------

_C15_S4 = _pstep(
    "choose", "Only one branch runs",
    "A boolean condition, and the branch it does not choose never evaluated at all.",
    """
```ts
case "if": {
  const cond = evaluate(e.cond, env);
  if (!cond.ok) {
    return cond;
  }
  if (typeof cond.value !== "boolean") {
    return { ok: false, error: "error: if condition must be a boolean" };
  }
  if (cond.value) {
    return evaluate(e.whenTrue, env);
  }
  return evaluate(e.whenFalse, env);
}
```

### The condition must be a boolean

`if 1 then 2 else 3` is refused. JavaScript would call `1` "truthy" and pick the
first branch; module 14 already decided this language does not coerce, and a
condition is no exception. The error names the problem directly.

### The branch not chosen never runs

This is the most important line in the case, and it is easy to get wrong:

```ts
if (cond.value) {
  return evaluate(e.whenTrue, env);
}
return evaluate(e.whenFalse, env);
```

Evaluate the condition, then evaluate **one** branch. Not both-then-choose. The
difference shows the moment a branch can fail:

```
if false then 1 / 0 else 2
```

Evaluating both branches first would report `division by zero` for a division
the program explicitly chose not to do. Evaluating only the chosen one gives `2`.
That laziness is what makes a conditional useful as a *guard* —
`if d == 0 then 0 else n / d` — and every language with a conditional works this
way.

### Dynamic types

`if true then true else 1` is fine: the branches have different types, and the
value is whichever one runs. The language checks types as it evaluates (module
14), not before. A statically-typed language would reject this program; it is a
real design choice, and the stretch list explores the other side of it.
""",
    """
```bash
$ echo 'if false then 1 / 0 else 2' | node calc.ts
2
$ echo 'if 1 then 2 else 3' | node calc.ts
error: if condition must be a boolean
$ echo 'let x = 5; if x > 3 then x * 2 else 0' | node calc.ts
10
```

Phase 4 is done: variables, statements, booleans and decisions.
""",
    pitfalls=[
        "Evaluating both branches before choosing. `if false then 1 / 0 else 2` reports a division the program never asked for.",
        "Truthiness: `if (cond.value)` without the `typeof` check. It compiles — any value can be an `if` condition in TypeScript — and `if 1 then …` quietly picks the first branch.",
        "Evaluating the condition after the branches. Its error would come second, contradicting the left-to-right rule of module 11.",
    ],
    warmup=[
        _pq("What does `if false then 1 / 0 else 2` print?",
            ["`2` — the `then` branch is never evaluated",
             "`error: division by zero`",
             "`Infinity`",
             "`1`"],
            0,
            "Only the chosen branch runs."),
    ],
    exercises=[
        _pex("calc-m15-choose-1", "A condition must be a boolean",
             "After evaluating the condition, refuse anything that is not a "
             "boolean with `error: if condition must be a boolean`.",
             _C15_FULL,
             '      if (typeof cond.value !== "boolean") {\n        return { ok: false, error: "error: if condition must be a boolean" };\n      }',
             _C15_TESTS,
             ["`typeof` again — this time checking for `\"boolean\"`.",
              "No coercion: a number is not a condition.",
              "`if (typeof cond.value !== \"boolean\") { return { ok: false, error: \"error: if condition must be a boolean\" }; }`"]),
        _pfix("calc-m15-choose-fix1", "A division nobody asked for",
              "`if false then 1 / 0 else 2` says `error: division by zero`. The "
              "program chose the `else` branch; the `then` branch should never "
              "have been touched.",
              _c15(evaluate=_C15_EVAL.replace(
                  "      if (cond.value) {\n        return evaluate(e.whenTrue, env);\n      }\n      return evaluate(e.whenFalse, env);\n",
                  "      const whenTrue = evaluate(e.whenTrue, env);\n      if (!whenTrue.ok) {\n        return whenTrue;\n      }\n"
                  "      const whenFalse = evaluate(e.whenFalse, env);\n      if (!whenFalse.ok) {\n        return whenFalse;\n      }\n"
                  "      if (cond.value) {\n        return whenTrue;\n      }\n      return whenFalse;\n")),
              _C15_FULL,
              _C15_TESTS,
              ["How many branches are evaluated before the choice is made?",
               "Both — so a failure in the branch not taken still wins.",
               "Choose first, then evaluate only the chosen branch."],
              difficulty="Medium"),
    ],
    quiz=[
        _pq("Why does `if d == 0 then 0 else n / d` need lazy branches?",
            ["When `d` is 0 the division branch must not run at all, or it fails with division by zero",
             "For speed only",
             "Because `==` is lazy",
             "It does not need them"],
            0,
            "A conditional is a guard only if the guarded branch is skipped."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C15_FINAL = _pch(
    "calc-m15-build", "Module 15 build — the language can decide", "Hard",
    "Write the `if` expression end to end — the parser's case and the "
    "evaluator:\n\n"
    "* in `parsePrimary`: `if` EXPR `then` EXPR `else` EXPR, with `expected "
    "'then'` and `expected 'else'`\n"
    "* `evaluate` — module 14's, with an `if` case: a boolean condition, and "
    "only the chosen branch evaluated\n\n"
    "Tests include `if false then 1 / 0 else 2` and `if true then 1 else 2 + 10`.",
    _C15_FULL,
    _C15_EVAL.rstrip("\n"),
    _C15_TESTS,
    ["The `if` case: evaluate `e.cond`, pass a failure up, `typeof … !== \"boolean\"` is an error.",
     "Then `if (cond.value)` — return the evaluation of ONE branch.",
     "Keep every other case, and the `never` default."],
)
_C15_FINAL["prompt"] = (
    "Write `evaluate` for the whole language — numbers, booleans, variables, "
    "negation, `if` and binary operators:\n\n"
    "* `num` through `checked`; `bool` as itself; `var` from the environment\n"
    "* `neg` refuses a boolean\n"
    "* `if` needs a boolean condition, and evaluates ONLY the branch it picks\n"
    "* `binary` evaluates left then right and hands both to `apply`\n"
    "* a `never` default\n\n"
    "Tests include `if false then 1 / 0 else 2` and `if 1 then 2 else 3`."
)


_CALC_MODULES.append(_pmod(
    key="calc-if", number=15, phase="lang",
    title="`if` as an expression",
    what="a conditional that has a value, and the type rule that forces",
    goal="Evaluate `if 2 < 3 then 10 else 20`.",
    why=_C15_WHY,
    est_minutes=45,
    builds_on=["calc-never", "calc-booleans"],
    concepts=["conditional expressions", "mandatory else", "reserved keywords",
              "lazy evaluation", "no truthiness", "dynamic typing",
              "exhaustiveness as a to-do list"],
    deliverable="`echo 'if 2 < 3 then 10 else 20' | node calc.ts` prints `10`, "
                "`if false then 1 / 0 else 2` prints `2`, and a missing `else` is "
                "a parse error.",
    objectives=[
        "Explain the difference between a conditional statement and a conditional expression",
        "Say why `else` is mandatory, and what problem that removes",
        "Add three keywords and a node, and check the compiler lists exactly the right switches",
        "Parse `if … then … else …` as a primary with full-expression branches",
        "Evaluate only the chosen branch, and give the input that shows why",
        "Refuse a non-boolean condition, consistent with module 14's no-coercion rule",
    ],
    brief=_C15_BRIEF,
    syntax=_C15_SYNTAX,
    steps=[_C15_S1, _C15_S2, _C15_S3, _C15_S4],
    final_build=_C15_FINAL,
    acceptance=[
        "`echo 'if 2 < 3 then 10 else 20' | node calc.ts` prints `10`.",
        "`echo '1 + if true then 2 else 3' | node calc.ts` prints `3`.",
        "`echo 'if false then 1 / 0 else 2' | node calc.ts` prints `2`.",
        "`echo 'if true then 1' | node calc.ts` prints `error: expected 'else' but found end of input`.",
        "`echo 'if 1 then 2 else 3' | node calc.ts` prints `error: if condition must be a boolean`.",
        "Adding `IfToken`, `ThenToken`, `ElseToken` and `If` produced compile errors in `describe` and `evaluate` and nowhere else.",
    ],
    manual_test="""
```bash
echo 'if 2 < 3 then 10 else 20'                       | node calc.ts   # 10
echo 'let x = 5; if x > 3 then x * 2 else 0'          | node calc.ts   # 10
echo '1 + if true then 2 else 3'                      | node calc.ts   # 3
echo 'if 1 > 2 then 1 else if 2 > 1 then 2 else 3'    | node calc.ts   # 2
echo 'if false then 1 / 0 else 2'                     | node calc.ts   # 2
echo 'if true then 1'                                 | node calc.ts   # expected 'else'
echo 'if 1 then 2 else 3'                             | node calc.ts   # condition must be a boolean
```

Do the module 10 exam for real, if you have not: start from your module 14
`calc.ts`, add ONLY the four new types, and compile. Count the errors and the
functions they are in. Four errors, two functions — and not `apply`, and not
`execute`.

Phase 4's outcome was `let x = 4; x * x > 10`. Try something it did not promise:

```bash
echo 'let n = 7; let d = 0; if d == 0 then 0 else n / d' | node calc.ts   # 0
```

A guard. The division never runs.
""",
    reference="""// calc.ts — module 15
//
// `if c then a else b` is an EXPRESSION — a primary, with a value — so the
// `else` is mandatory: an expression must always have a value. The condition
// must be a boolean (no truthiness), and ONLY the chosen branch is evaluated, so
// `if false then 1 / 0 else 2` is 2. Each branch is a full expression, so the
// last one reaches as far right as it can.
""" + _C15_FULL,
    stretch=[
        "Check types BEFORE running: write `typeOf(e, env)` that returns `\"number\"`, `\"boolean\"` or an error, and reject `if c then 1 else true` because its branches disagree. You have just started writing a static type checker.",
        "Add `and` and `or`, short-circuiting — which is the same laziness as `if`. Can you implement `a and b` as `if a then b else false`, as a rewrite in the parser?",
        "Allow `if` without `else` as a STATEMENT only (`if x > 3 then let y = 1`). What does the grammar need, and what does a statement-level `if` evaluate to?",
        "Add a `match` expression: `match x with 1 then 10 | 2 then 20 else 0`. It is a chain of `if`s; decide whether it deserves its own node.",
    ],
    glossary=[
        _pgloss("conditional expression", "An `if` with a value — whichever branch its condition selects."),
        _pgloss("dangling else", "The ambiguity of which `if` an `else` belongs to when `else` is optional. Impossible here, since every `if` has one."),
        _pgloss("lazy evaluation", "Evaluating only what is needed. Only the chosen branch of an `if` is evaluated."),
        _pgloss("truthiness", "Treating non-booleans as true or false (JavaScript: `if (1)`). This language refuses."),
        _pgloss("dynamic typing", "Checking types while running. Branches of an `if` may have different types; the one that runs decides."),
    ],
    cheatsheet="""
```
primary  =  number | bool | name | "(" expr ")" | "if" expr "then" expr "else" expr
```

```ts
type If = { kind: "if"; cond: Expr; whenTrue: Expr; whenFalse: Expr };

case "if": {
  const cond = evaluate(e.cond, env);
  if (!cond.ok) { return cond; }
  if (typeof cond.value !== "boolean") {
    return { ok: false, error: "error: if condition must be a boolean" };
  }
  if (cond.value) { return evaluate(e.whenTrue, env); }   // ONE branch
  return evaluate(e.whenFalse, env);
}
```

| Input | Output |
|---|---|
| `if 2 < 3 then 10 else 20` | `10` |
| `if true then 1 else 2 + 10` | `1` — the else is `2 + 10` |
| `if false then 1 / 0 else 2` | `2` |
| `if true then 1` | `error: expected 'else' but found end of input` |
| `if 1 then 2 else 3` | `error: if condition must be a boolean` |

| Symptom | Cause |
|---|---|
| `if false then 1/0 else 2` fails | both branches evaluated |
| `… else 2 + 10` gives 11 | else branch parsed with a smaller rule than `parseExpr` |
| `if 1 then …` picks a branch | no `typeof` check on the condition |
""",
    self_check=[
        "Can you explain why `if` here is an expression and what that forces?",
        "Can you list the compile errors adding `if` produced, and say why `apply` was not among them?",
        "Can you write the `if` case of `parsePrimary` and say why every part uses `parseExpr`?",
        "Can you give an input that shows whether a conditional is lazy?",
        "Can you explain why `if true then true else 1` is allowed?",
    ],
    review=[
        _pq("What does `1 + if true then 2 else 3` print?",
            ["`3`",
             "An error",
             "`2`",
             "`4`"],
            0,
            "An `if` is a primary — an operand like any other."),
        _pq("Why is there no dangling-else problem in this language?",
            ["Every `if` must have exactly one `else`, so there is never a question which `if` an `else` belongs to",
             "Because `else` is optional",
             "Because `if` must be bracketed",
             "There is one"],
            0,
            "A rule forced by expressions, with a free benefit."),
        _pq("`if false then 1 / 0 else 2` — why `2`?",
            ["Only the chosen branch is evaluated; the division never runs",
             "Because division by zero is 0",
             "Because `false` is 0",
             "It prints an error"],
            0,
            "Laziness makes a conditional a guard."),
        _pq("What does `if 1 then 2 else 3` report?",
            ["`error: if condition must be a boolean`",
             "`2`",
             "`3`",
             "`error: unexpected '1'`"],
            0,
            "No truthiness, consistent with module 14."),
        _pq("Adding `If` produced errors only in `describe` and `evaluate`. What does that show?",
            ["Every switch over the grown unions has a `never` check, and nothing else depends on them",
             "That module 10 was skipped",
             "That `if` is broken",
             "Nothing"],
            0,
            "The compiler complained in exactly the right places."),
    ],
    milestone="Phase 4 is done. `calc.ts` is a language — names, statements, "
              "booleans, comparison and a conditional that is an expression — and "
              "growing it produced a precise to-do list from the compiler rather "
              "than a bug report. Phase 5 makes it usable by someone who is not you.",
))
